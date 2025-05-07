import jwt
import json
import aiohttp
from typing import List
import common.config.const as const
import common.config.config as config
from common.config.config import (
    RAW_REPOSITORY_URL,
    CHAT_REPOSITORY,
    CYODA_ENTITY_TYPE_EDGE_MESSAGE,
)

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
    clone_repo,
    validate_token,
)
from entity.chat.model.chat import ChatEntity
from entity.model import FlowEdgeMessage, ChatMemory, ModelConfig
from services.factory import entity_service, cyoda_auth_service, chat_lock, ai_agent  # imported from services/__init__.py

class ChatService:
    def __init__(self):
        self.entity_service     : EntityService = entity_service
        self.auth_service                          = cyoda_auth_service
        self.chat_lock                             = chat_lock
        self.ai_agent                              = ai_agent

    # public methods used by routes
    async def list_chats(self, user_id: str) -> List[dict]:
        if not user_id:
            raise InvalidTokenException("Invalid token")

        chats = await self._get_entities_by_user_name_and_workflow_name(user_id, const.CHAT_MODEL_NAME)
        if not user_id.startswith("guest."):
            transfers = await self._get_entities_by_user_name(user_id, const.TRANSFER_CHATS_ENTITY)
            if transfers:
                guest_id = transfers[0]["guest_user_id"]
                chats += await self._get_entities_by_user_name_and_workflow_name(guest_id, const.CHAT_MODEL_NAME)

        return [{
            "technical_id": c.technical_id,
            "name": c.name,
            "description": c.description,
            "date": c.date,
        } for c in chats]

    async def create_chat(self, user_id: str, req_data: dict) -> dict:
        if user_id.startswith("guest."):
            existing = await self._get_entities_by_user_name_and_workflow_name(user_id, const.CHAT_MODEL_NAME)
            if len(existing) >= config.MAX_GUEST_CHATS:
                raise GuestChatsLimitExceededException("Max guest chats limit reached")

        init_q = req_data.get("name", "")
        if len(init_q.encode("utf-8")) > config.MAX_TEXT_SIZE:
            return {"error": "Answer size exceeds 1MB limit"}

        # 1) create greeting
        edge_id = await self.entity_service.add_item(
            token=self.auth_service,
            entity_model=const.FLOW_EDGE_MESSAGE_MODEL_NAME,
            entity_version=config.ENTITY_VERSION,
            entity={
                "current_transition": "",
                "current_state": "",
                "type": "notification",
                "publish": True,
                "consumed": True,
                "notification": "Hi! I'm Cyoda 🧚. Let me take a look at your question…"
            },
            meta={"type": CYODA_ENTITY_TYPE_EDGE_MESSAGE}
        )
        greeting = FlowEdgeMessage(user_id=user_id, type="notification",
                                   publish=True, edge_message_id=edge_id)

        # 2) new memory
        memory_id = await self.entity_service.add_item(
            token=self.auth_service,
            entity_model=const.MEMORY_MODEL_NAME,
            entity_version=config.ENTITY_VERSION,
            entity=ChatMemory.model_validate({"messages": {}})
        )

        # 3) build ChatEntity
        chat = ChatEntity.model_validate({
            "user_id": user_id,
            "chat_id": "",
            "date": current_timestamp(),
            "name": init_q[:25] + "…" if len(init_q) > 25 else init_q,
            "description": req_data.get("description"),
            "chat_flow": {"current_flow": [], "finished_flow": []},
            "current_transition": "",
            "current_state": "",
            "workflow_name": const.CHAT_MODEL_NAME,
            "failed": "false",
            "transitions_memory": {"conditions": {}, "current_iteration": {}, "max_iteration": {}},
            "memory_id": memory_id,
        })

        # 4) echo back user question
        ans_id = await add_answer_to_finished_flow(
            entity_service=self.entity_service,
            answer=init_q,
            cyoda_auth_service=self.auth_service
        )
        chat.chat_flow.finished_flow.extend([
            FlowEdgeMessage(type="answer", publish=True,
                            edge_message_id=ans_id, consumed=False, user_id=user_id),
            greeting
        ])

        # 5) persist and respond
        tech_id = await self.entity_service.add_item(
            token=self.auth_service,
            entity_model=const.CHAT_MODEL_NAME,
            entity_version=config.ENTITY_VERSION,
            entity=chat
        )
        return {"message":"Chat created", "technical_id": tech_id, "answer_technical_id": ans_id}

    async def get_chat(self, auth_header: str, technical_id: str) -> dict:
        chat = await self._get_chat_for_user(auth_header, technical_id)
        dialog = await self._process_message(chat.chat_flow.finished_flow, auth_header, [])
        return {
            "technical_id": technical_id,
            "name": chat.name,
            "description": chat.description,
            "date": chat.date,
            "dialogue": dialog
        }

    async def delete_chat(self, auth_header: str, technical_id: str) -> dict:
        await self._get_chat_for_user(auth_header, technical_id)
        #todo Unresolved attribute reference 'delete_item' for class 'EntityService'
        await self.entity_service.delete_item(
            token=self.auth_service,
            entity_model=const.CHAT_MODEL_NAME,
            entity_version=config.ENTITY_VERSION,
            technical_id=technical_id,
            meta={}
        )
        return {"message":"Chat deleted", "technical_id": technical_id}

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
            return {"error":"Answer size exceeds 1MB limit"}
        return await self._submit_answer_helper(answer, chat)

    async def submit_answer(self, auth_header, technical_id, answer, user_file):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        message = await get_user_message(answer, user_file)
        if user_file and user_file.content_length > config.MAX_FILE_SIZE:
            return {"error": f"File size exceeds {config.MAX_FILE_SIZE} limit"}
        return await self._submit_answer_helper(message, chat, user_file)

    async def approve(self, auth_header, technical_id):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        return await self._submit_answer_helper(const.APPROVE, chat)

    async def rollback(self, auth_header, technical_id):
        chat = await self._get_chat_for_user(auth_header, technical_id)
        await self._rollback_dialogue_script(technical_id, chat)
        return {"message":"Successfully restarted the workflow"}

    # ─── Private helpers ─────────────────────────────────────────────────────

    async def _get_chat_for_user(self, auth_header, technical_id):
        user_id = self._get_user_id(auth_header)
        if not user_id:
            raise InvalidTokenException()

        chat = await self.entity_service.get_item(
            token=self.auth_service,
            entity_model=const.CHAT_MODEL_NAME,
            entity_version=config.ENTITY_VERSION,
            technical_id=technical_id
        )

        if not chat and CHAT_REPOSITORY == "local":
            async with self.chat_lock:
                chat = await self.entity_service.get_item(
                    token=self.auth_service,
                    entity_model=const.CHAT_MODEL_NAME,
                    entity_version=config.ENTITY_VERSION,
                    technical_id=technical_id
                )
                if not chat:
                    await clone_repo(chat_id=technical_id)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{RAW_REPOSITORY_URL}/{technical_id}/entity/chat.json") as resp:
                            data = await resp.text()
                    chat = ChatEntity.model_validate(json.loads(data))
                    if not chat:
                        raise ChatNotFoundException()
                    await self.entity_service.add_item(
                        token=self.auth_service,
                        entity_model=const.CHAT_MODEL_NAME,
                        entity_version=config.ENTITY_VERSION,
                        entity=chat
                    )
        elif not chat:
            raise ChatNotFoundException()

        await self._validate_chat_owner(chat, user_id)
        return chat

    async def _validate_chat_owner(self, chat, user_id):
        if chat.user_id == user_id:
            return

        is_guest_to_reg = chat.user_id.startswith("guest.") and not user_id.startswith("guest.")
        if not is_guest_to_reg:
            raise InvalidTokenException()

        ents = await self._get_entities_by_user_name(user_id, const.TRANSFER_CHATS_ENTITY)
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
            token=self.auth_service,
            entity_model=model,
            entity_version=config.ENTITY_VERSION,
            condition={
                "cyoda": {
                    "operator": "AND",
                    "conditions": [{
                        "jsonPath":"$.user_id","operatorType":"EQUALS",
                        "value":user_id,"type":"simple"
                    }],
                    "type":"group"
                },
                "local":{"key":"user_id","value":user_id}
            }
        )

    async def _get_entities_by_user_name_and_workflow_name(self, user_id, model):
        return await self.entity_service.get_items_by_condition(
            token=self.auth_service,
            entity_model=model,
            entity_version=config.ENTITY_VERSION,
            condition={
                "cyoda": {
                    "operator":"AND",
                    "conditions":[
                        {"jsonPath":"$.user_id","operatorType":"EQUALS","value":user_id,"type":"simple"},
                        {"jsonPath":"$.workflow_name","operatorType":"EQUALS","value":const.CHAT_MODEL_NAME,"type":"simple"}
                    ],
                    "type":"group"
                },
                "local":{"key":"user_id","value":user_id}
            }
        )

    async def _submit_question_helper(self, auth_header, technical_id, chat, question, user_file=None):
        if not question:
            return {"error":"Invalid entity"}, 400
        if config.MOCK_AI == "true":
            return {"message":"mock ai answer"}, 200
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
            messages=[{"role":"user","content":question}]
        )
        return {"message": result}, 200

    async def _submit_answer_helper(self, answer, chat, user_file=None):
        if chat.user_id.startswith("guest.") and len(chat.chat_flow.finished_flow) > const.MAX_GUEST_CHAT_MESSAGES:
            return {"error":"Maximum messages reached"}, 403
        if len(chat.chat_flow.finished_flow) > const.MAX_CHAT_MESSAGES:
            return {"error":"Maximum messages reached"}, 403
        valid, val_answer = self._validate_answer(answer, user_file)
        if not valid:
            return {"message":val_answer}, 400

        edge_id, transitioned = await trigger_manual_transition(
            entity_service=self.entity_service,
            chat=chat,
            answer=val_answer,
            user_file=user_file,
            cyoda_auth_service=self.auth_service,
            transition=const.PROCESS_USER_INPUT_TRANSITION
        )
        if transitioned:
            return {"answer_technical_id": edge_id}, 200
        return {"message": const.DESIGN_IN_PROGRESS_WARNING}, 409

    async def _rollback_dialogue_script(self, technical_id: str, chat: ChatEntity):
        async def _traverse(entity: ChatEntity, tid: str, is_root: bool=False) -> bool:
            targets = getattr(entity, "child_entities", []) + getattr(entity, "scheduled_entities", [])
            if entity.current_state.startswith(const.LOCKED_CHAT) and targets:
                for child_id in reversed(targets):
                    child = await self.entity_service.get_item(
                        token=self.auth_service,
                        entity_model=const.CHAT_MODEL_NAME,
                        entity_version=config.ENTITY_VERSION,
                        technical_id=child_id
                    )
                    has_kids = bool(getattr(child, "child_entities", None) or getattr(child, "scheduled_entities", None))
                    if child.current_state.startswith(const.LOCKED_CHAT) and has_kids:
                        if await _traverse(child, child_id):
                            return True
                    if not child.current_state.startswith(const.LOCKED_CHAT):
                        await _launch_transition(self.entity_service, child.technical_id, self.auth_service, None, const.MANUAL_RETRY_TRANSITION)
                        if chat.chat_flow.finished_flow and not chat.chat_flow.finished_flow[-1].consumed:
                            await _launch_transition(self.entity_service, child.technical_id, self.auth_service, None, const.PROCESS_USER_INPUT_TRANSITION)
                        return True
                if is_root:
                    for t in (const.MANUAL_RETRY_TRANSITION, const.UNLOCK_CHAT_TRANSITION, const.PROCESS_USER_INPUT_TRANSITION):
                        await _launch_transition(self.entity_service, tid, self.auth_service, None, t)
                    return True
                return False

            if not entity.current_state.startswith(const.LOCKED_CHAT) or is_root:
                for t in (const.MANUAL_RETRY_TRANSITION, const.UNLOCK_CHAT_TRANSITION, const.PROCESS_USER_INPUT_TRANSITION):
                    await _launch_transition(self.entity_service, tid, self.auth_service, None, t)
                return True
            return False

        return await _traverse(chat, technical_id, is_root=True)

    def _validate_answer(self, answer, user_file):
        if not answer:
            return (True, "Consider the file contents") if user_file else (False, "Invalid entity")
        return True, answer

    async def _process_message(self, finished_flow: List[FlowEdgeMessage], auth_header, dialogue: list) -> list:
        for msg in finished_flow:
            if msg.type in ("question","notification","answer") and msg.publish:
                content = await self.entity_service.get_item(
                    token=self.auth_service,
                    entity_model=const.FLOW_EDGE_MESSAGE_MODEL_NAME,
                    entity_version=config.ENTITY_VERSION,
                    technical_id=msg.edge_message_id,
                    meta={"type": CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                )
                content["technical_id"] = msg.edge_message_id
                dialogue.append(content)

            if msg.type == "child_entities":
                content = await self.entity_service.get_item(
                    token=self.auth_service,
                    entity_model=const.FLOW_EDGE_MESSAGE_MODEL_NAME,
                    entity_version=config.ENTITY_VERSION,
                    technical_id=msg.edge_message_id,
                    meta={"type":CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                )
                for child_id in content.get("child_entities", []):
                    child = await self.entity_service.get_item(
                        token=self.auth_service,
                        entity_model=const.CHAT_MODEL_NAME,
                        entity_version=config.ENTITY_VERSION,
                        technical_id=child_id
                    )
                    await self._process_message(child.chat_flow.finished_flow, auth_header, dialogue)
        return dialogue
