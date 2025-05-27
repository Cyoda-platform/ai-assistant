import logging
import random

import jwt
from typing import List, Tuple
import common.config.const as const
from common.config.config import config

from common.exception.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    ChatNotFoundException,
    GuestChatsLimitExceededException,
)
from common.service.entity_service_interface import EntityService
from common.utils.chat_util_functions import (
    get_user_message,
    add_answer_to_finished_flow,
    trigger_manual_transition,
    _launch_transition,
)
from common.utils.utils import (
    current_timestamp,
    validate_token, send_cyoda_request, get_current_timestamp_num,
)
from entity.chat.chat import ChatEntity
from entity.model import FlowEdgeMessage, ChatMemory, ModelConfig, AgenticFlowEntity

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, entity_service, cyoda_auth_service, chat_lock, ai_agent):
        self.entity_service: EntityService = entity_service
        self.chat_lock = chat_lock
        self.ai_agent = ai_agent
        self.cyoda_auth_service = cyoda_auth_service

    async def transfer_chats(self, guest_token, auth_header):
        guest_user_id = self._get_user_id(auth_header=f"Bearer {guest_token}")
        user_id = self._get_user_id(auth_header=auth_header)

        transfer_chats_entities = await self._get_entities_by_user_name(user_id=user_id, model=const.ModelName.TRANSFER_CHATS_ENTITY)

        if transfer_chats_entities:
            raise GuestChatsLimitExceededException("Sorry, your guest chats have already been transferred. Only one guest session is allowed.")

        transfer_chats_entity = {
            "user_id": user_id,
            "guest_user_id": guest_user_id
        }
        await self.entity_service.add_item(token=self.cyoda_auth_service,
                                      entity_model=const.ModelName.TRANSFER_CHATS_ENTITY,
                                      entity_version=config.ENTITY_VERSION,
                                      entity=transfer_chats_entity)

    # public methods used by routes
    # todo stream chats not to load all of them into memory
    async def list_chats(self, user_id: str) -> List[dict]:
        if not user_id:
            raise InvalidTokenException("Invalid token")

        chats = await self._get_entities_by_user_name_and_workflow_name(user_id, const.ModelName.CHAT_ENTITY.value)
        if not user_id.startswith("guest."):
            transfers = await self._get_entities_by_user_name(user_id, const.ModelName.TRANSFER_CHATS_ENTITY.value)
            if transfers:
                guest_id = transfers[0]["guest_user_id"]
                chats += await self._get_entities_by_user_name_and_workflow_name(guest_id,
                                                                                 const.ModelName.CHAT_ENTITY.value)

        return [{
            "technical_id": c.technical_id,
            "name": c.name,
            "description": c.description,
            "date": c.date,
        } for c in chats]

    async def add_chat(self, user_id: str, req_data: dict) -> dict:
        if user_id.startswith("guest."):
            existing = await self._get_entities_by_user_name_and_workflow_name(user_id,
                                                                               const.ModelName.CHAT_ENTITY.value)
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
                message="Hi! I'm Cyoda 🧚. Let me take a look at your question…",
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
        chat = ChatEntity.model_validate({
            "user_id": user_id,
            "chat_id": "",
            "date": current_timestamp(),
            "name": init_q[:name_length] + "…" if len(init_q) > name_length else init_q,
            "description": req_data.get("description"),
            "chat_flow": {"current_flow": [], "finished_flow": []},
            "current_transition": "",
            "current_state": "",
            "workflow_name": const.ModelName.CHAT_ENTITY.value,
            "failed": "false",
            "transitions_memory": {"conditions": {}, "current_iteration": {}, "max_iteration": {}},
            "memory_id": memory_id,
            "last_modified": last_modified
        })

        # 4) echo back user question
        ans_id, last_modified = await add_answer_to_finished_flow(
            entity_service=self.entity_service,
            answer=init_q,
            cyoda_auth_service=self.cyoda_auth_service
        )
        chat.chat_flow.finished_flow.extend([
            FlowEdgeMessage(type="answer",
                            publish=True,
                            edge_message_id=ans_id,
                            consumed=False,
                            user_id=user_id,
                            last_modified=last_modified),
            greeting
        ])

        # 5) persist and respond
        tech_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            entity=chat
        )
        return {"message": "Chat created", "technical_id": tech_id, "answer_technical_id": ans_id}

    async def get_chat(self, auth_header: str, technical_id: str) -> dict:
        chat = await self._get_chat_for_user(auth_header, technical_id)
        dialogue, child_entities = await self._process_message(finished_flow=chat.chat_flow.finished_flow,
                                                               auth_header=auth_header,
                                                               dialogue=[],
                                                               child_entities=set())
        # dialogue = self._post_process_dialogue(dialogue)
        entities_data = await self._get_entities_processing_data(technical_id=technical_id,
                                                                 child_entities=child_entities)
        return {
            "technical_id": technical_id,
            "name": chat.name,
            "description": chat.description,
            "date": chat.date,
            "dialogue": dialogue,
            "entities_data": entities_data
        }

    async def delete_chat(self, auth_header: str, technical_id: str) -> dict:
        await self._get_chat_for_user(auth_header, technical_id)
        # todo Unresolved attribute reference 'delete_item' for class 'EntityService'
        await self.entity_service.delete_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            technical_id=technical_id,
            meta={}
        )
        return {"message": "Chat deleted", "technical_id": technical_id}

    async def submit_text_question(self, auth_header, technical_id, question):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        return await self._submit_question_helper(auth_header, technical_id, chat, question)

    async def submit_question(self, auth_header, technical_id, question, user_file):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        if user_file and user_file.content_length > config.MAX_FILE_SIZE:
            return {"error": f"File size exceeds {config.MAX_FILE_SIZE} limit"}
        return await self._submit_question_helper(auth_header, technical_id, chat, question, user_file)

    async def submit_text_answer(self, auth_header, technical_id, answer):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        if len(answer.encode("utf-8")) > config.MAX_TEXT_SIZE:
            return {"error": "Answer size exceeds 1MB limit"}
        return await self._submit_answer_helper(answer, chat)

    async def submit_answer(self, auth_header, technical_id, answer, user_file):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        message = await get_user_message(answer, user_file)
        if user_file and user_file.content_length > config.MAX_FILE_SIZE:
            return {"error": f"File size exceeds {config.MAX_FILE_SIZE} limit"}
        return await self._submit_answer_helper(message, chat, user_file)

    async def approve(self, auth_header, technical_id):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        return await self._submit_answer_helper(const.Notifications.APPROVE.value, chat)

    async def rollback(self, auth_header, technical_id):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        await self._rollback_dialogue_script(technical_id, chat)
        return {"message": "Successfully restarted the workflow"}

    # ─── Private helpers ─────────────────────────────────────────────────────

    async def _get_chat_for_user(self, auth_header, technical_id):
        user_id = self._get_user_id(auth_header)
        if not user_id:
            raise InvalidTokenException()

        chat = await self.entity_service.get_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            technical_id=technical_id
        )

        # if not chat and config.CHAT_REPOSITORY == "local":
        #     async with self.chat_lock:
        #         chat = await self.entity_service.get_item(
        #             token=self.cyoda_auth_service,
        #             entity_model=const.ModelName.CHAT_ENTITY.value,
        #             entity_version=config.ENTITY_VERSION,
        #             technical_id=technical_id
        #         )
        #         if not chat:
        #             await clone_repo(chat_id=technical_id)
        #             async with httpx.AsyncClient() as client:
        #                 response = await client.get(f"{config.RAW_REPOSITORY_URL}/{technical_id}/entity/chat.json")
        #                 response.raise_for_status()  # Optional: ensures error is raised for non-2xx
        #                 data = response.text
        #             chat = ChatEntity.model_validate(json.loads(data))
        #             if not chat:
        #                 raise ChatNotFoundException()
        #             await self.entity_service.add_item(
        #                 token=self.cyoda_auth_service,
        #                 entity_model=const.ModelName.CHAT_ENTITY.value,
        #                 entity_version=config.ENTITY_VERSION,
        #                 entity=chat
        #             )
        if not chat:
            raise ChatNotFoundException()

        await self._validate_chat_owner(chat, user_id)
        return chat

    async def _validate_chat_owner(self, chat, user_id):
        if not config.ENABLE_AUTH:
            return
        if chat.user_id == user_id:
            return

        is_guest_to_reg = chat.user_id.startswith("guest.") and not user_id.startswith("guest.")
        if not is_guest_to_reg:
            raise InvalidTokenException()

        ents = await self._get_entities_by_user_name(user_id, const.ModelName.TRANSFER_CHATS_ENTITY.value)
        if not ents or ents[0]["guest_user_id"] != chat.user_id:
            raise InvalidTokenException()

    def _get_user_id(self, auth_header):
        if not auth_header:
            raise InvalidTokenException()
        token = auth_header.split(" ")[1]
        if not token:
            raise InvalidTokenException()
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get("caas_org_id")
            if not user_id:
                raise InvalidTokenException()
            if user_id.startswith("guest."):
                validate_token(token)
            return user_id
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except jwt.InvalidTokenError:
            return None

    async def _get_entities_by_user_name(self, user_id, model):
        return await self.entity_service.get_items_by_condition(
            token=self.cyoda_auth_service,
            entity_model=model,
            entity_version=config.ENTITY_VERSION,
            condition={
                "cyoda": {
                    "operator": "AND",
                    "conditions": [{
                        "jsonPath": "$.user_id", "operatorType": "EQUALS",
                        "value": user_id, "type": "simple"
                    }],
                    "type": "group"
                },
                "local": {"key": "user_id", "value": user_id}
            }
        )

    async def _get_entities_by_user_name_and_workflow_name(self, user_id, model):
        return await self.entity_service.get_items_by_condition(
            token=self.cyoda_auth_service,
            entity_model=model,
            entity_version=config.ENTITY_VERSION,
            condition={
                "cyoda": {
                    "operator": "AND",
                    "conditions": [
                        {"jsonPath": "$.user_id", "operatorType": "EQUALS", "value": user_id, "type": "simple"},
                        {"jsonPath": "$.workflow_name", "operatorType": "EQUALS",
                         "value": const.ModelName.CHAT_ENTITY.value, "type": "simple"}
                    ],
                    "type": "group"
                },
                "local": {"key": "user_id", "value": user_id}
            }
        )

    async def _submit_question_helper(self, auth_header, technical_id, chat, question, user_file=None):
        if not question:
            return {"error": "Invalid entity"}, 400
        if config.MOCK_AI == "true":
            return {"message": "mock ai answer"}, 200
        if user_file:
            question = await get_user_message(message=question, user_file=user_file)

        result = await self.ai_agent.run_agent(
            methods_dict=None,
            cls_instance=None,
            entity=chat,
            technical_id=technical_id,
            tools=None,
            model=ModelConfig(),
            tool_choice=None,
            messages=[{"role": "user", "content": question}]
        )
        return {"message": result}, 200

    async def _submit_answer_helper(self, answer, chat, user_file=None):
        if chat.user_id.startswith("guest.") and len(chat.chat_flow.finished_flow) > const.MAX_GUEST_CHAT_MESSAGES:
            return {"error": "Maximum messages reached"}, 403
        if len(chat.chat_flow.finished_flow) > const.MAX_CHAT_MESSAGES:
            return {"error": "Maximum messages reached"}, 403
        valid, val_answer = self._validate_answer(answer, user_file)
        if not valid:
            return {"message": val_answer}, 400

        next_transition = const.TransitionKey.MANUAL_APPROVE.value \
            if answer == const.Notifications.APPROVE.value \
            else const.TransitionKey.PROCESS_USER_INPUT.value

        edge_id, transitioned = await trigger_manual_transition(
            entity_service=self.entity_service,
            chat=chat,
            answer=val_answer,
            user_file=user_file,
            cyoda_auth_service=self.cyoda_auth_service,
            transition=next_transition
        )
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
                    if child.current_state.startswith(const.TransitionKey.LOCKED_CHAT.value) and has_kids:
                        if await _traverse(child, child_id):
                            return True
                    if not child.current_state.startswith(const.TransitionKey.LOCKED_CHAT.value):
                        await _launch_transition(self.entity_service, child.technical_id, self.cyoda_auth_service, None,
                                                 const.TransitionKey.MANUAL_RETRY.value)
                        if chat.chat_flow.finished_flow and chat.chat_flow.finished_flow[-1].type == "answer" and not \
                                chat.chat_flow.finished_flow[-1].consumed:
                            await _launch_transition(self.entity_service, child.technical_id, self.cyoda_auth_service,
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

    def _validate_answer(self, answer, user_file):
        if not answer:
            return (True, "Consider the file contents") if user_file else (False, "Invalid entity")
        return True, answer

    async def _process_message(self, finished_flow: List[FlowEdgeMessage], auth_header, dialogue: list,
                               child_entities: set) -> Tuple[
        list, set]:

        for msg in finished_flow:
            if msg.type in ("question", "notification", "answer") and msg.publish:
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
                    if not content.message.rstrip().endswith(approve_msg.rstrip()):
                        content.message = f"{content.message.rstrip()}\n\n{approve_msg}"
                if content.type == "answer" and content.message == const.Notifications.APPROVE.value:
                    content.message = random.choice(list(const.ApproveAnswer)).value
                message_content = content.model_dump()
                #todo - for backwards compatibility - remove
                message_content[content.type] = content.message
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
                                                child_entities=child_entities)
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
        ]

        entities: List[AgenticFlowEntity] = []
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
                if entity.workflow_name == const.ModelName.CHAT_ENTITY.value:
                    last_step = entity.chat_flow.finished_flow[-1] if entity.chat_flow.finished_flow else None
                    if last_step and last_step.type == "answer" and not last_step.consumed:
                        await _launch_transition(
                            self.entity_service,
                            entity.technical_id,
                            self.cyoda_auth_service,
                            None,
                            const.TransitionKey.PROCESS_USER_INPUT.value,
                        )
            except Exception as e:
                logger.exception(f"Failed to rollback workflow for entity {entity.technical_id}: {e}")




