from common.config.config import ENTITY_VERSION, CYODA_ENTITY_TYPE_EDGE_MESSAGE
from common.config.conts import LOCKED_CHAT, CHAT_MODEL_NAME, FLOW_EDGE_MESSAGE_MODEL_NAME, \
    EDGE_MESSAGE_STORE_MODEL_NAME
from common.util.file_reader import read_file_content
from entity.chat.model.chat import ChatEntity
from entity.model.model import FlowEdgeMessage


async def trigger_manual_transition(entity_service, chat: ChatEntity, answer, cyoda_auth_service, user_file=None):
    user_answer = await get_user_message(message=answer, user_file=user_file) if user_file else answer
    edge_message_id = await add_answer_to_finished_flow(entity_service=entity_service, answer=user_answer, chat=chat,
                                                        cyoda_auth_service=cyoda_auth_service)
    # Helper to process a chat entity: add answer, increment iteration, and launch transition.
    async def process_entity(entity: ChatEntity, technical_id: str):
        entity.chat_flow.finished_flow.append(FlowEdgeMessage(type="answer",
                                             publish=True,
                                             edge_message_id=edge_message_id,
                                             consumed=False,
                                             user_id=chat.user_id))
        _increment_iteration(chat=entity, answer=user_answer)
        await _launch_transition(entity=entity, technical_id=technical_id, entity_service=entity_service, cyoda_auth_service=cyoda_auth_service)

    # If the chat is locked, try processing its child entities.
    if chat.child_entities and chat.current_state == LOCKED_CHAT:
        has_active_child = False

        # Iterate through child entities in reverse order.
        for child_id in reversed(chat.child_entities):
            child_entity = await entity_service.get_item(
                token=cyoda_auth_service,
                entity_model=CHAT_MODEL_NAME,
                entity_version=ENTITY_VERSION,
                technical_id=child_id
            )
            # If the child entity is not locked, process its transition.
            if child_entity.current_state != LOCKED_CHAT:
                await process_entity(child_entity, child_id)
                has_active_child = True
            else:
                # Abort transition if a child is locked.
                break

        # If no active (unlocked) child entities were processed, process the main chat.
        if not has_active_child:
            # unlock
            #todo refactor workflow, remove next line, dont pass entity to update
            chat.locked=False
            await _launch_transition(entity=chat, technical_id=chat.technical_id, entity_service=entity_service, cyoda_auth_service=cyoda_auth_service)

            await process_entity(entity=chat, technical_id=chat.technical_id)
    else:
        # If the chat is not locked, process it directly.
        await process_entity(chat, chat.technical_id)
    return edge_message_id


async def add_answer_to_finished_flow(entity_service, answer: str, chat: ChatEntity, cyoda_auth_service):
    flow_message_content = {
        "type": "answer",
        "answer": answer,
        "publish": True
    }
    edge_message_id = await entity_service.add_item(token=cyoda_auth_service,
                                                    entity_model=FLOW_EDGE_MESSAGE_MODEL_NAME,
                                                    entity_version=ENTITY_VERSION,
                                                    entity=flow_message_content,
                                                    meta={"type": CYODA_ENTITY_TYPE_EDGE_MESSAGE})

    return edge_message_id


async def get_user_message(message, user_file):
    if user_file:
        file_contents = read_file_content(user_file)
        message = f"{message}: {file_contents}" if message else file_contents
    return message


def _increment_iteration(chat, answer):
    pass
    #if answer == APPROVE:
        #pass
        # todo!
        # transition = chat.current_transition
        # chat.transitions_memory.get("current_iteration")[transition] = MAX_ITERATION + 1


async def _launch_transition(entity_service, technical_id, cyoda_auth_service, entity=None):
    next_transitions = await entity_service.get_transitions(token=cyoda_auth_service,
                                                            meta={},
                                                            technical_id=technical_id)
    # todo!!!
    next_transition = next_transitions[0]
    await entity_service.update_item(token=cyoda_auth_service,
                                     entity_model=CHAT_MODEL_NAME,
                                     entity_version=ENTITY_VERSION,
                                     technical_id=technical_id,
                                     entity=entity,
                                     meta={"update_transition": next_transition})


class _SafeDict(dict):
    def __missing__(self, key):
        # leave unknown placeholders untouched
        return "{" + key + "}"

async def enrich_config_message(entity_service, cyoda_auth_service, entity, config_message):
    # grab your caches (or empty if None)
    cache = dict(entity.workflow_cache or {})
    edge_store = entity.edge_messages_store or {}

    # nothing here? bail out
    if not cache and not edge_store:
        return config_message

    # if you still want to pull in all edge‑store items:
    for key, edge_id in edge_store.items():
        result = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model=EDGE_MESSAGE_STORE_MODEL_NAME,
            entity_version=ENTITY_VERSION,
            technical_id=edge_id,
            meta={"type": CYODA_ENTITY_TYPE_EDGE_MESSAGE},
        )
        cache[key] = str(result)

    # now do one pass: each line.format_map(cache_with_fallback)
    safe_cache = _SafeDict(cache)
    enriched = [
        line.format_map(safe_cache)
        for line in config_message.get("content", [])
    ]
    config_message["content"] = enriched
    return config_message

