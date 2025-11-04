import logging
import random
from datetime import datetime

from typing import List, Tuple
import common.config.const as const
from common.config.config import config

from common.exception.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    ChatNotFoundException,
    GuestChatsLimitExceededException,
)
from common.schemas.workflow_schema import WORKFLOW_RESPONSE_FORMAT
from common.service.entity_service_interface import EntityService
from common.utils.chat_util_functions import (
    get_user_message,
    add_answer_to_finished_flow,
    trigger_manual_transition,
    _launch_transition,
)
from common.utils.utils import (
    current_timestamp,
    send_cyoda_request, get_current_timestamp_num,
)
from entity.chat.chat import ChatEntity, ChatBusinessEntity
from entity.model import FlowEdgeMessage, ChatMemory, ModelConfig, AgenticFlowEntity, AIMessage, ChatFlow, \
    TransitionsMemory, WorkflowEntity
from services.user_answer_validation_service import UserAnswerValidationService

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, entity_service, cyoda_auth_service, chat_lock, ai_agent, data_service):
        self.entity_service: EntityService = entity_service
        self.chat_lock = chat_lock
        self.ai_agent = ai_agent
        self.cyoda_auth_service = cyoda_auth_service
        self.data_service = data_service
        self.validation_service = UserAnswerValidationService(entity_service, cyoda_auth_service)

    async def transfer_chats(self, guest_token, auth_header):
        from common.utils.auth_utils import get_user_id
        guest_user_id = await get_user_id(auth_header=f"Bearer {guest_token}")
        user_id = await get_user_id(auth_header=auth_header)

        transfer_chats_entities = await self.data_service.get_entities_by_user_name(user_id=user_id,
                                                                                    model=const.ModelName.TRANSFER_CHATS_ENTITY.value)

        transfer_chats_entity = {
            "user_id": user_id,
            "guest_user_id": guest_user_id
        }
        chat_transferred_to_different_account = any(
            entity.get("user_id") != user_id and entity.get("guest_user_id") == guest_user_id
            for entity in transfer_chats_entities
        )
        if chat_transferred_to_different_account:
            raise GuestChatsLimitExceededException(
                "Sorry, your guest chats have already been transferred to a different account. Please log in with your previous account.")

        # Check if an entity with matching user_id and guest_user_id already exists
        already_exists = any(
            entity.get("user_id") == user_id and entity.get("guest_user_id") == guest_user_id
            for entity in transfer_chats_entities
        )

        # Add only if not already present
        if not already_exists:
            await self.entity_service.add_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.TRANSFER_CHATS_ENTITY.value,
                entity_version=config.ENTITY_VERSION,
                entity=transfer_chats_entity
            )

    # public methods used by routes
    # todo stream chats not to load all of them into memory
    async def list_chats(self, user_id: str, is_super: bool = False, target_user_id: str = None) -> List[dict]:
        if not user_id:
            raise InvalidTokenException("Invalid token")

        # Determine which user's chats to retrieve
        if is_super:
            # Super user requesting chats - handle both all chats and specific user
            return await self._list_all_chats(target_user_id=target_user_id)
        else:
            # Regular user requesting their own chats
            query_user_id = user_id

        chats = await self.data_service.get_entities_by_user_name(user_id=query_user_id,
                                                                  model=const.ModelName.CHAT_BUSINESS_ENTITY.value)
        transfer_chats = []
        if not query_user_id.startswith("guest."):
            transfers = await self.data_service.get_entities_by_user_name(user_id=query_user_id,
                                                                          model=const.ModelName.TRANSFER_CHATS_ENTITY.value)

            guest_user_ids = set()

            for transfer in transfers:
                guest_id = transfer["guest_user_id"]
                if guest_id not in guest_user_ids and guest_id.startswith("guest."):
                    transfer_chats += await self.data_service.get_entities_by_user_name(
                        user_id=guest_id,
                        model=const.ModelName.CHAT_BUSINESS_ENTITY.value
                    )
                    guest_user_ids.add(guest_id)
        if transfer_chats:
            chats += transfer_chats
            def parse_chat_date(chat):
                try:
                    return datetime.strptime(chat.date, "%Y-%m-%dT%H:%M:%S.%fZ")
                except (TypeError, ValueError):
                    return datetime.min  # fallback if date is missing or malformed

            chats = sorted(chats, key=parse_chat_date, reverse=True)
        return [{
            "technical_id": c.technical_id,
            "name": c.name,
            "description": c.description,
            "date": c.date,
        } for c in chats]

    async def add_chat(self, user_id: str, req_data: dict, user_files=None, user_file=None) -> dict:
        # Convert single file to user_files for consistent processing
        if user_file and not user_files:
            user_files = [user_file]
        if user_id.startswith("guest."):
            existing = await self.data_service.get_entities_by_user_name_and_workflow_name(user_id=user_id,
                                                                                           model=const.ModelName.CHAT_ENTITY.value,
                                                                                           workflow_name=const.ModelName.CHAT_ENTITY.value)
            if len(existing) >= config.MAX_GUEST_CHATS:
                raise GuestChatsLimitExceededException("Max guest chats limit reached")

        init_q = req_data.get("name", "")
        if len(init_q.encode("utf-8")) > config.MAX_TEXT_SIZE:
            return {"error": "Answer size exceeds 1MB limit"}

        # 1) create greeting
        last_modified = get_current_timestamp_num()
        edge_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
            entity_version=config.ENTITY_VERSION,
            entity=FlowEdgeMessage(
                current_transition="",
                current_state="",
                type="notification",
                publish=True,
                consumed=True,
                message=const.CYODA_WELCOME_MESSAGE,
                last_modified=last_modified
            ),
            meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
        )
        greeting = FlowEdgeMessage(user_id=user_id,
                                   type="notification",
                                   publish=True,
                                   last_modified=last_modified,
                                   edge_message_id=edge_id)

        # 2) new memory
        memory_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_MEMORY.value,
            entity_version=config.ENTITY_VERSION,
            entity=ChatMemory.model_validate({"messages": {}, "last_modified": last_modified})
        )

        # 3) build ChatEntity
        name_length = 50

        chat = ChatEntity(
            user_id=user_id,
            date=current_timestamp(),
            chat_flow=ChatFlow(current_flow=[], finished_flow=[]),
            current_transition="",
            current_state="",
            workflow_name=const.ModelName.CHAT_ENTITY.value,
            failed=False,
            transitions_memory=TransitionsMemory(conditions={}, current_iteration={}, max_iteration={}),
            memory_id=memory_id,
            last_modified=last_modified
        )

        # 4) echo back user question with validation
        processed_answer, file_blob_ids = await self.validation_service.validate_and_process_answer(
            answer=init_q,
            user_files=user_files,
            user_id=user_id
        )
        ans_id, last_modified = await add_answer_to_finished_flow(
            entity_service=self.entity_service,
            answer=processed_answer,
            cyoda_auth_service=self.cyoda_auth_service,
            file_blob_ids=file_blob_ids
        )

        flow_edge_message = FlowEdgeMessage(
            type="answer",
            publish=True,
            edge_message_id=ans_id,
            consumed=False,
            user_id=user_id,
            last_modified=last_modified
        )

        # Add file blob references if available
        if file_blob_ids:
            flow_edge_message.file_blob_ids = file_blob_ids

        chat.chat_flow.finished_flow.extend([flow_edge_message, greeting])

        # 5) persist and respond
        chat_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            entity=chat
        )
        chat_wrapper = ChatBusinessEntity(user_id=user_id,
                                          chat_id=chat_id,
                                          date=current_timestamp(),
                                          name=init_q[:name_length] + "…" if len(init_q) > name_length else init_q,
                                          workflow_name=const.ModelName.CHAT_BUSINESS_ENTITY.value,
                                          description=req_data.get("description"))
        tech_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_BUSINESS_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            entity=chat_wrapper
        )
        return {"message": "Chat created", "technical_id": tech_id, "answer_technical_id": ans_id}

    async def get_chat(self, auth_header: str, technical_id: str, is_super: bool = False) -> dict:
        chat_business_entity = await self._get_business_chat_for_user(auth_header=auth_header,
                                                                      technical_id=technical_id,
                                                                      is_super=is_super)
        chat: ChatEntity = await self.entity_service.get_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            technical_id=chat_business_entity.chat_id
        )
        dialogue, child_entities = await self._process_message(finished_flow=chat.chat_flow.finished_flow,
                                                               auth_header=auth_header,
                                                               dialogue=[],
                                                               child_entities=set(),
                                                               chat_technical_id=technical_id)
        # dialogue = self._post_process_dialogue(dialogue)
        entities_data = await self._get_entities_processing_data(technical_id=chat.technical_id,
                                                                 child_entities=child_entities)
        return {
            "technical_id": technical_id,
            "name": chat_business_entity.name,
            "description": chat_business_entity.description,
            "date": chat_business_entity.date,
            "dialogue": dialogue,
            "entities_data": entities_data
        }

    async def download_file(self, auth_header: str, technical_id: str, blob_id: str) -> dict:
        """
        Download a file by blob ID from a chat.

        Args:
            auth_header: Authentication header
            technical_id: Chat technical ID
            blob_id: Blob edge message ID

        Returns:
            Dictionary containing file data and metadata or error
        """
        try:
            # Skip auth verification for now (auth_header can be None)
            if auth_header:
                await self._get_business_chat_for_user(auth_header=auth_header, technical_id=technical_id)

            # Retrieve the blob edge message
            blob_message: FlowEdgeMessage = await self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                entity_version=config.ENTITY_VERSION,
                technical_id=blob_id,
                meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )

            if not blob_message:
                return {"error": "File not found"}

            if blob_message.type != "file_blob":
                return {"error": "Invalid file type"}

            # Extract file metadata
            metadata = blob_message.metadata or {}
            filename = metadata.get("filename", "download")
            content_type = metadata.get("content_type", "application/octet-stream")
            file_size = metadata.get("file_size", 0)
            encoding = metadata.get("encoding", "base64")

            # Decode file content
            if encoding == "base64":
                import base64
                try:
                    file_content = base64.b64decode(blob_message.message)
                except Exception as e:
                    return {"error": f"Failed to decode file content: {str(e)}"}
            else:
                file_content = blob_message.message.encode('utf-8') if isinstance(blob_message.message, str) else blob_message.message

            return {
                "filename": filename,
                "content_type": content_type,
                "file_size": file_size,
                "content": file_content
            }

        except Exception as e:
            return {"error": f"Failed to download file: {str(e)}"}

    async def delete_chat(self, auth_header: str, technical_id: str) -> dict:
        # verify chat belongs to the user
        chat_business_entity: ChatBusinessEntity = await self._get_business_chat_for_user(auth_header=auth_header,
                                                                                          technical_id=technical_id)
        await self.entity_service.update_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_BUSINESS_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            technical_id=chat_business_entity.technical_id,
            entity=chat_business_entity,
            meta={const.TransitionKey.UPDATE.value: const.TransitionKey.DELETE.value}
        )
        return {"message": "Chat deleted", "technical_id": technical_id}

    async def rename_chat(self, auth_header: str, technical_id: str, chat_name: str, chat_description: str) -> dict:
        chat_business_entity: ChatBusinessEntity = await self._get_business_chat_for_user(auth_header=auth_header,
                                                                                          technical_id=technical_id)
        if chat_name:
            chat_business_entity.name = chat_name
        if chat_description:
            chat_business_entity.description = chat_description
        await self.entity_service.update_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_BUSINESS_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            technical_id=chat_business_entity.technical_id,
            entity=chat_business_entity,
            meta={const.TransitionKey.UPDATE.value: const.TransitionKey.UPDATE.value}
        )
        return {"message": "Chat renamed", "technical_id": technical_id}

    async def submit_text_question(self, question):
        return await self._submit_question_helper(question)

    async def submit_question(self, question, user_file=None, user_files=None):
        # Convert single file to user_files for consistent processing
        if user_file and not user_files:
            user_files = [user_file]
            user_file = None  # Clear single file since we moved it to user_files
        # Handle multiple files
        files_to_process = user_files if user_files else []

        # Check file size limits for all files
        for file in files_to_process:
            if file and file.content_length > config.MAX_FILE_SIZE:
                filename = getattr(file, 'filename', 'unknown')
                return {"error": f"File '{filename}' size exceeds {config.MAX_FILE_SIZE} limit"}

        return await self._submit_question_helper(question, user_files)

    async def submit_workflow_question(self, question, workflow, user_file=None, user_files=None):
        # Convert single file to user_files for consistent processing
        if user_file and not user_files:
            user_files = [user_file]
            user_file = None  # Clear single file since we moved it to user_files
        # Handle multiple files
        files_to_process = user_files if user_files else []

        # Check file size limits for all files
        for file in files_to_process:
            if file and file.content_length > config.MAX_FILE_SIZE:
                filename = getattr(file, 'filename', 'unknown')
                return {"error": f"File '{filename}' size exceeds {config.MAX_FILE_SIZE} limit"}

        # Enhance question with workflow context
        workflow_question = f"Question: {question}. My current workflow is {workflow}. Response schema: {WORKFLOW_RESPONSE_FORMAT}. Please return a only valid JSON without any extra text or markdown."

        return await self._submit_question_helper(
            question=workflow_question if workflow else question,
            user_files=user_files,
            response_format=WORKFLOW_RESPONSE_FORMAT
        )

    async def submit_canvas_question(self, chat_id, question, response_type, context):
        """
        Submit a canvas question to generate entity, workflow, app config, or environment config.

        Args:
            chat_id: Optional chat ID to associate with this question
            question: Natural language question
            response_type: Type of config to generate (entity_json, workflow_json, app_config_json, environment_json)
            context: Additional context (app_name, existing_entities, language, etc.)

        Returns:
            Response with message and hook structure
        """
        import json
        from pathlib import Path
        from common.schemas.canvas_schemas import get_response_format

        # Handle 'text' response type (for Code tab) - just return a helpful text response
        if response_type == 'text':
            # For text responses, we don't need structured output
            prompt_path = Path('workflow_configs/agents/configs/canvas_assistant/prompts/system_prompt.md')
            try:
                with open(prompt_path, 'r') as f:
                    system_prompt = f.read().strip()
            except Exception as e:
                logger.error(f"Failed to load system prompt: {e}")
                system_prompt = "You are a helpful AI assistant."

            # Enhance question with context
            context_str = ""
            if context:
                context_parts = []
                if context.get('app_name'):
                    context_parts.append(f"Application: {context['app_name']}")
                if context.get('active_tab'):
                    context_parts.append(f"Active tab: {context['active_tab']}")
                if context_parts:
                    context_str = f"\n\nContext:\n" + "\n".join(context_parts)

            enhanced_question = f"{question}{context_str}"

            try:
                result = await self.ai_agent.run_agent(
                    methods_dict=None,
                    cls_instance=None,
                    entity=None,
                    technical_id=chat_id or "canvas_question",
                    tools=None,
                    model=ModelConfig(model_name='gpt-4o'),
                    tool_choice=None,
                    messages=[
                        AIMessage(role="system", content=system_prompt),
                        AIMessage(role="user", content=enhanced_question)
                    ],
                    response_format=None  # No structured output for text
                )

                return {
                    "message": result,
                    # No hook for text responses - just plain text
                }
            except Exception as e:
                logger.exception(f"AI agent failed for text response: {e}")
                return {
                    "error": "Failed to generate response",
                    "details": {
                        "message": str(e)
                    }
                }

        # Map response_type to hook type (for structured JSON responses)
        hook_type_map = {
            'entity_json': 'entity_config',
            'workflow_json': 'workflow_config',
            'app_config_json': 'app_config',
            'environment_json': 'environment_config',
            'requirement_json': 'requirement_config'
        }

        hook_type = hook_type_map.get(response_type)
        if not hook_type:
            return {
                "error": "Invalid response type",
                "details": {
                    "message": f"Unknown response_type: {response_type}"
                }
            }

        # Get response format from schemas
        try:
            response_format = get_response_format(response_type)
        except ValueError as e:
            logger.error(f"Invalid response_type: {e}")
            return {
                "error": "Invalid response type",
                "details": {
                    "message": str(e)
                }
            }
        except Exception as e:
            logger.error(f"Failed to load schema for {response_type}: {e}")
            return {
                "error": "Failed to generate configuration",
                "details": {
                    "message": f"Could not load schema: {str(e)}"
                }
            }

        # Enhance question with context
        context_str = ""
        if context:
            context_parts = []
            if context.get('app_name'):
                context_parts.append(f"Application: {context['app_name']}")
            if context.get('existing_entities'):
                context_parts.append(f"Existing entities: {', '.join(context['existing_entities'])}")
            if context.get('existing_workflows'):
                context_parts.append(f"Existing workflows: {', '.join(context['existing_workflows'])}")
            if context.get('language'):
                context_parts.append(f"Language: {context['language']}")

            if context_parts:
                context_str = f"\n\nContext:\n" + "\n".join(context_parts)

        enhanced_question = f"{question}{context_str}"

        # Load system prompt
        prompt_path = Path('workflow_configs/agents/configs/canvas_assistant/prompts/system_prompt.md')
        try:
            with open(prompt_path, 'r') as f:
                system_prompt = f.read().strip()
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            system_prompt = "You are a helpful AI assistant for generating application configurations."

        # Call AI agent with canvas assistant config
        try:
            result = await self.ai_agent.run_agent(
                methods_dict=None,
                cls_instance=None,
                entity=None,
                technical_id=chat_id or "canvas_question",
                tools=None,
                model=ModelConfig(model_name='gpt-4o'),
                tool_choice=None,
                messages=[
                    AIMessage(role="system", content=system_prompt),
                    AIMessage(role="user", content=enhanced_question)
                ],
                response_format=response_format
            )

            # Parse JSON result
            try:
                config_data = json.loads(result) if isinstance(result, str) else result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                return {
                    "error": "Failed to generate configuration",
                    "details": {
                        "message": "AI response was not valid JSON",
                        "suggestion": "Please try rephrasing your question with more specific details"
                    }
                }

            # Build response with hook
            return {
                "message": f"I've created a {hook_type.replace('_', ' ')} based on your requirements.",
                "hook": {
                    "type": hook_type,
                    "action": "preview",
                    "data": config_data
                }
            }

        except Exception as e:
            logger.exception(f"Failed to generate canvas config: {e}")
            return {
                "error": "Failed to generate configuration",
                "details": {
                    "message": str(e),
                    "suggestion": "Please try rephrasing your question or providing more context"
                }
            }

    async def submit_text_answer(self, auth_header, technical_id, answer, user_files=None, user_file=None):
        # Convert single file to user_files for consistent processing
        if user_file and not user_files:
            user_files = [user_file]

        chat = await self._get_chat_for_user(auth_header, technical_id)

        # Check file size limits for all files
        if user_files:
            for file in user_files:
                if file and file.content_length > config.MAX_FILE_SIZE:
                    filename = getattr(file, 'filename', 'unknown')
                    return {"error": f"File '{filename}' size exceeds {config.MAX_FILE_SIZE} limit"}

        if len(answer.encode("utf-8")) > config.MAX_TEXT_SIZE:
            return {"error": "Answer size exceeds 1MB limit"}
        return await self._submit_answer_helper(answer, chat, user_files=user_files)

    async def submit_answer(self, auth_header, technical_id, answer, user_file=None, user_files=None):
        # Convert single file to user_files for consistent processing
        if user_file and not user_files:
            user_files = [user_file]
            user_file = None  # Clear single file since we moved it to user_files

        chat = await self._get_chat_for_user(auth_header, technical_id)

        # Handle multiple files
        files_to_process = user_files if user_files else []

        # Check file size limits for all files
        for file in files_to_process:
            if file and file.content_length > config.MAX_FILE_SIZE:
                filename = getattr(file, 'filename', 'unknown')
                return {"error": f"File '{filename}' size exceeds {config.MAX_FILE_SIZE} limit"}

        # Don't process files into message here - let validation service handle file content as answer
        # Only use get_user_message for the final processed message after validation
        return await self._submit_answer_helper(answer, chat, user_files=user_files)

    async def approve(self, auth_header, technical_id):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        return await self._submit_answer_helper(const.Notifications.APPROVE.value, chat, user_files=None)

    async def rollback(self, auth_header, technical_id):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        await self._rollback_dialogue_script(technical_id, chat)
        return {"message": "Successfully restarted the workflow"}

    # ─── Private helpers ─────────────────────────────────────────────────────

    async def _get_business_chat_for_user(self, auth_header, technical_id, is_super: bool = False):
        from common.utils.auth_utils import get_user_info
        user_id, token_is_super = await get_user_info(auth_header)
        if not user_id:
            raise InvalidTokenException()

        chat_business_entity = await self.entity_service.get_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_BUSINESS_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            technical_id=technical_id
        )

        if not chat_business_entity:
            raise ChatNotFoundException()

        # Super users can access any chat if both request and token indicate super status
        if is_super and token_is_super:
            return chat_business_entity

        await self._validate_chat_owner(chat_business_entity, user_id)
        return chat_business_entity

    async def _get_chat_for_user(self, auth_header, technical_id):
        chat_business_entity = await self._get_business_chat_for_user(auth_header=auth_header,
                                                                      technical_id=technical_id)
        chat = await self.entity_service.get_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            technical_id=chat_business_entity.chat_id
        )
        return chat

    async def _validate_chat_owner(self, chat, user_id):
        if not config.ENABLE_AUTH:
            return
        if chat.user_id == user_id:
            return

        if not chat.user_id.startswith('guest.'):
            raise InvalidTokenException()

        is_guest_to_reg = chat.user_id.startswith("guest.") and not user_id.startswith("guest.")
        if not is_guest_to_reg:
            raise InvalidTokenException()

        transfer_chats = await self.data_service.get_entities_by_user_name(user_id, const.ModelName.TRANSFER_CHATS_ENTITY.value)
        has_transfer = any(transfer_chat['guest_user_id'] == chat.user_id for transfer_chat in transfer_chats)
        if not transfer_chats or not has_transfer:
            raise InvalidTokenException()



    async def _list_all_chats(self, target_user_id: str = None) -> List[dict]:
        """
        List all chats from all users (super user functionality).

        Args:
            target_user_id: Optional user ID to filter chats for specific user
        """
        if target_user_id:
            # Filter chats for specific user (including their transfer chats)
            all_chats = await self.data_service.get_entities_by_user_name(
                user_id=target_user_id,
                model=const.ModelName.CHAT_BUSINESS_ENTITY.value
            )

            # Add transfer chats for the specific user (same logic as regular list_chats)
            transfer_chats = []
            if not target_user_id.startswith("guest."):
                transfers = await self.data_service.get_entities_by_user_name(
                    user_id=target_user_id,
                    model=const.ModelName.TRANSFER_CHATS_ENTITY.value
                )

                guest_user_ids = set()
                for transfer in transfers:
                    guest_id = transfer["guest_user_id"]
                    if guest_id not in guest_user_ids and guest_id.startswith("guest."):
                        transfer_chats += await self.data_service.get_entities_by_user_name(
                            user_id=guest_id,
                            model=const.ModelName.CHAT_BUSINESS_ENTITY.value
                        )
                        guest_user_ids.add(guest_id)

            if transfer_chats:
                all_chats += transfer_chats
                # Sort by date (same logic as regular list_chats)
                def parse_chat_date(chat):
                    try:
                        return datetime.strptime(chat.date, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except (TypeError, ValueError):
                        return datetime.min
                all_chats.sort(key=parse_chat_date, reverse=True)
        else:
            # Get all chat business entities without user filtering
            all_chats = await self.entity_service.get_items(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.CHAT_BUSINESS_ENTITY.value,
                entity_version=config.ENTITY_VERSION
            )

            # For super users getting ALL chats, also get ALL transfer chats
            # This ensures complete visibility across the system
            all_transfer_entities = await self.entity_service.get_items(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.TRANSFER_CHATS_ENTITY.value,
                entity_version=config.ENTITY_VERSION
            )

            # Get all guest chats that have been transferred
            guest_chats = []
            processed_guests = set()
            for transfer in all_transfer_entities:
                guest_id = getattr(transfer, "guest_user_id", "")
                if guest_id and guest_id.startswith("guest.") and guest_id not in processed_guests:
                    guest_user_chats = await self.data_service.get_entities_by_user_name(
                        user_id=guest_id,
                        model=const.ModelName.CHAT_BUSINESS_ENTITY.value
                    )
                    guest_chats.extend(guest_user_chats)
                    processed_guests.add(guest_id)

            if guest_chats:
                all_chats.extend(guest_chats)

        # Format the response similar to regular list_chats
        formatted_chats = []
        if not all_chats:
            return formatted_chats
        for chat in all_chats:
            formatted_chats.append({
                "technical_id": chat.technical_id,
                "name": getattr(chat, 'name', ''),
                "description": getattr(chat, 'description', ''),
                "date": getattr(chat, 'date', ''),
                "user_id": getattr(chat, 'user_id', ''),
                "last_modified": getattr(chat, 'last_modified', '')
            })

        return formatted_chats

    async def _submit_question_helper(self, question, user_files=None, response_format=None):
        if not question:
            return {"error": "Invalid entity"}, 400
        if config.MOCK_AI == "true":
            return {"message": "mock ai answer"}, 200
        if user_files:
            question = await get_user_message(message=question, user_files=user_files)

        # Mock entity and technical_id for compatibility (not needed for simple question submission)
        result = await self.ai_agent.run_agent(
            methods_dict=None,
            cls_instance=None,
            entity=None,
            technical_id="mock_technical_id",
            tools=None,
            model=ModelConfig(model_name="gpt-5-mini"),
            tool_choice=None,
            messages=[AIMessage(role="user", content=question)],
            response_format=response_format
        )
        return {"message": result}, 200

    async def _submit_answer_helper(self, answer, chat, user_files=None):
        if chat.user_id.startswith("guest.") and len(chat.chat_flow.finished_flow) > const.MAX_GUEST_CHAT_MESSAGES:
            return {"error": "Maximum messages reached"}, 403
        if len(chat.chat_flow.finished_flow) > const.MAX_CHAT_MESSAGES:
            return {"error": "Maximum messages reached"}, 403
        # Validation is now handled by the UserAnswerValidationService in trigger_manual_transition
        # No need for separate validation here

        next_transition = const.TransitionKey.MANUAL_APPROVE.value \
            if answer == const.Notifications.APPROVE.value \
            else const.TransitionKey.PROCESS_USER_INPUT.value

        transitioned = False
        try:

            edge_id, transitioned = await trigger_manual_transition(
                entity_service=self.entity_service,
                chat=chat,
                answer=answer,  # Pass original answer, let validation service handle it
                user_files=user_files,
                cyoda_auth_service=self.cyoda_auth_service,
                transition=next_transition,
                validation_service=self.validation_service
            )
        except Exception as e:
            logger.exception(f"Failed to process answer: {e}")
        if transitioned:
            return {"answer_technical_id": edge_id}, 200
        return {"message": const.Notifications.DESIGN_PLEASE_WAIT.value}, 409

    async def _rollback_dialogue_script(self, technical_id: str, chat: ChatEntity):
        async def _traverse(entity: ChatEntity, tid: str, is_root: bool = False) -> bool:
            targets = getattr(entity, "child_entities", []) + getattr(entity, "scheduled_entities", [])
            if entity.current_state.startswith(const.TransitionKey.LOCKED_CHAT.value) and targets:
                for child_id in reversed(targets):
                    child = await self.entity_service.get_item(
                        token=self.cyoda_auth_service,
                        entity_model=const.ModelName.CHAT_ENTITY.value,
                        entity_version=config.ENTITY_VERSION,
                        technical_id=child_id
                    )
                    has_kids = bool(
                        getattr(child, "child_entities", None) or getattr(child, "scheduled_entities", None))
                    # todo check why child can be null
                    if child and isinstance(chat, WorkflowEntity):
                        if child.current_state and child.current_state.startswith(
                                const.TransitionKey.LOCKED_CHAT.value) and has_kids:
                            if await _traverse(child, child_id):
                                return True
                        if not child.current_state.startswith(const.TransitionKey.LOCKED_CHAT.value):
                            await _launch_transition(self.entity_service, child.technical_id, self.cyoda_auth_service,
                                                     None,
                                                     const.TransitionKey.MANUAL_RETRY.value)
                            if chat.chat_flow.finished_flow and chat.chat_flow.finished_flow[
                                -1].type == "answer" and not \
                                    chat.chat_flow.finished_flow[-1].consumed:
                                await _launch_transition(self.entity_service, child.technical_id,
                                                         self.cyoda_auth_service,
                                                         None,
                                                         const.TransitionKey.PROCESS_USER_INPUT.value)
                            return True
                if is_root:
                    for t in (const.TransitionKey.MANUAL_RETRY.value, const.TransitionKey.UNLOCK_CHAT.value,
                              const.TransitionKey.PROCESS_USER_INPUT.value):
                        await _launch_transition(self.entity_service, tid, self.cyoda_auth_service, None, t)
                    return True
                return False

            if not entity.current_state.startswith(const.TransitionKey.LOCKED_CHAT.value) or is_root:
                for t in (const.TransitionKey.MANUAL_RETRY.value, const.TransitionKey.UNLOCK_CHAT.value,
                          const.TransitionKey.PROCESS_USER_INPUT.value):
                    await _launch_transition(self.entity_service, tid, self.cyoda_auth_service, None, t)
                return True
            return False

        return await _traverse(chat, technical_id, is_root=True)



    async def _process_message(self, finished_flow: List[FlowEdgeMessage], auth_header, dialogue: list,
                               child_entities: set, chat_technical_id: str = None) -> Tuple[
        list, set]:

        for msg in finished_flow:
            if msg.type in ("question", "notification", "answer", const.UI_FUNCTION_PREFIX) and msg.publish:
                content: FlowEdgeMessage = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                    entity_version=config.ENTITY_VERSION,
                    technical_id=msg.edge_message_id,
                    meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                )
                content.technical_id = msg.edge_message_id
                if content.type == "question" and content.approve:
                    approve_msg = const.Notifications.APPROVE_INSTRUCTION_MESSAGE.value
                    if content.message and not content.message.rstrip().endswith(approve_msg.rstrip()):
                        content.message = f"{content.message.rstrip()}\n\n{approve_msg}"
                if content.type == "answer" and content.message == const.Notifications.APPROVE.value:
                    content.message = random.choice(list(const.ApproveAnswer)).value

                # Handle None messages gracefully (e.g., when long messages are saved as files only)
                if content.message is None:
                    content.message = ""
                message_content = content.model_dump()
                # todo - for backwards compatibility - remove
                message_content[content.type] = content.message

                # Add download URLs for file attachments
                if content.file_blob_ids:
                    message_content["file_downloads"] = []
                    for blob_id in content.file_blob_ids:
                        # Get blob metadata for filename
                        try:
                            blob_message: FlowEdgeMessage = await self.entity_service.get_item(
                                token=self.cyoda_auth_service,
                                entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                                entity_version=config.ENTITY_VERSION,
                                technical_id=blob_id,
                                meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                            )
                            if blob_message and blob_message.metadata:
                                filename = blob_message.metadata.get("filename", "download")
                                file_size = blob_message.metadata.get("file_size", 0)
                                content_type = blob_message.metadata.get("content_type", "application/octet-stream")
                            else:
                                filename = "download"
                                file_size = 0
                                content_type = "application/octet-stream"
                        except Exception:
                            filename = "download"
                            file_size = 0
                            content_type = "application/octet-stream"

                        message_content["file_downloads"].append({
                            "blob_id": blob_id,
                            "filename": filename,
                            "file_size": file_size,
                            "content_type": content_type,
                            "download_url": f"{config.API_PREFIX}/chats/{chat_technical_id}/files/{blob_id}" if chat_technical_id else f"/files/{blob_id}"
                        })

                # Add artificial message for empty messages with file downloads (temporary UI compatibility)
                if (not content.message or content.message.strip() == "") and content.file_blob_ids:
                    download_links = []
                    for file_download in message_content.get("file_downloads", []):
                        download_links.append(f"[{file_download['filename']}]({file_download['download_url']})")

                    if download_links:
                        artificial_message = f"Your request has been saved to a file. Click to download: {', '.join(download_links)}"
                        message_content["message"] = artificial_message
                        message_content[content.type] = artificial_message

                dialogue.append(message_content)

            if msg.type == "child_entities":
                content: FlowEdgeMessage = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                    entity_version=config.ENTITY_VERSION,
                    technical_id=msg.edge_message_id,
                    meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                )
                for child_id in content.message:
                    child_entities.add(child_id)
                    child = await self.entity_service.get_item(
                        token=self.cyoda_auth_service,
                        entity_model=const.ModelName.CHAT_ENTITY.value,
                        entity_version=config.ENTITY_VERSION,
                        technical_id=child_id
                    )
                    await self._process_message(finished_flow=child.chat_flow.finished_flow,
                                                auth_header=auth_header,
                                                dialogue=dialogue,
                                                child_entities=child_entities,
                                                chat_technical_id=chat_technical_id)
        return dialogue, child_entities

    async def _get_entities_processing_data(self, technical_id, child_entities):
        """
        Fetch processing data (versions and possible transitions) for a parent entity and its child entities.
        Returns a dict mapping entity IDs to their data.
        """
        try:
            # Retrieve processor remote address
            resp = await send_cyoda_request(
                cyoda_auth_service=self.cyoda_auth_service,
                method="get",
                path=const.ApiV1Endpoint.PROCESSOR_REMOTE_ADDRESS_PATH.value
            )
            nodes = resp.get('json', {}).get('pmNodes', [])
            if not nodes:
                raise ValueError('No processor nodes found')
            remote_address = nodes[0].get('hostname')

            # Prepare to fetch events for parent and child entities
            entity_events = {}
            entity_ids = [technical_id] + list(child_entities)

            for entity_id in entity_ids:
                path = const.ApiV1Endpoint.PROCESSOR_ENTITY_EVENTS_PATH.value.format(
                    processor_node_address=remote_address,
                    entity_class=const.JavaClasses.TREE_NODE_ENTITY.value,
                    entity_id=entity_id
                )
                resp = await send_cyoda_request(
                    cyoda_auth_service=self.cyoda_auth_service,
                    method="get",
                    path=path
                )
                data = resp.get('json', {})
                # todo need to improve - no need to fetch the whole entity to get workflow_name
                entity: AgenticFlowEntity = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.AGENTIC_FLOW_ENTITY.value,
                    entity_version=config.ENTITY_VERSION,
                    technical_id=entity_id
                )
                entity_events[entity_id] = {
                    'workflow_name': entity.workflow_name,
                    'entity_versions': data.get('entityVersions', []),
                    'next_transitions': data.get('possibleTransitions', [])
                }

            return entity_events

        except Exception as exc:
            # Log the error and re-raise for upstream handling
            logger.exception("Failed to retrieve processing data for entity %s: %s", technical_id, exc)
        return {}

    async def _get_entities_by_condition(self, model, condition):
        return await self.entity_service.get_items_by_condition(
            token=self.cyoda_auth_service,
            entity_model=model,
            entity_version=config.ENTITY_VERSION,
            condition=condition)

    async def rollback_failed_workflows(self) -> None:
        """
        Retry and clean up any workflows that have not failed but
        whose last update was more than 5 minutes ago.
        """
        # threshold: workflows modified more than 5 minutes ago
        # todo this timing logic is incomplete
        timestamp_threshold = get_current_timestamp_num(lower_timedelta=600)

        # Gather entities from both workflow types
        workflow_names = [
            const.ModelName.CHAT_ENTITY.value,
            const.ModelName.AGENTIC_FLOW_ENTITY.value,
            const.ModelName.SCHEDULER_ENTITY.value,
        ]

        entities: List[WorkflowEntity] = []
        condition = {
            "cyoda": {
                "type": "group",
                "operator": "AND",
                "conditions": [
                    {
                        "jsonPath": "$.failed",
                        "operatorType": "EQUALS",
                        "value": False,
                        "type": "simple",
                    },
                    {
                        "jsonPath": "$.last_modified",
                        "operatorType": "GREATER_THAN",
                        "value": timestamp_threshold,
                        "type": "simple",
                    },
                ],
            }
        }

        for workflow_name in workflow_names:
            try:
                fetched = await self._get_entities_by_condition(
                    model=workflow_name,
                    condition=condition,
                )
                entities.extend(fetched)
            except Exception as e:
                logger.exception(e)
        for entity in entities:
            try:
                await _launch_transition(
                    self.entity_service,
                    entity.technical_id,
                    self.cyoda_auth_service,
                    None,
                    const.TransitionKey.MANUAL_RETRY.value,
                )
                # if entity.workflow_name == const.ModelName.CHAT_ENTITY.value:
                #     last_step = entity.chat_flow.finished_flow[-1] if entity.chat_flow.finished_flow else None
                #     if last_step and last_step.type == "answer" and not last_step.consumed:
                #         await _launch_transition(
                #             self.entity_service,
                #             entity.technical_id,
                #             self.cyoda_auth_service,
                #             None,
                #             const.TransitionKey.PROCESS_USER_INPUT.value,
                #         )
            except Exception as e:
                logger.exception(f"Failed to rollback workflow for entity {entity.technical_id}: {e}")
