import logging
import common.config.const as const
from typing import Tuple

from common.config.config import config
from common.utils.file_reader import read_file_content
from entity.chat.model.chat import ChatEntity
from entity.model import FlowEdgeMessage

logger = logging.getLogger(__name__)


async def trigger_manual_transition(
        entity_service,
        chat: ChatEntity,
        answer,
        cyoda_auth_service,
        user_file=None,
        transition=None
) -> Tuple[str, bool]:
    # Resolve the user's answer
    user_answer = (
        await get_user_message(message=answer, user_file=user_file)
        if user_file
        else answer
    )

    # Append to finished_flow and get the edge ID
    edge_message_id = await add_answer_to_finished_flow(
        entity_service=entity_service,
        answer=user_answer,
        cyoda_auth_service=cyoda_auth_service
    )

    # Shared “answer + increment + launch” logic
    async def process_entity(entity: ChatEntity, technical_id: str, process_entity_transition=None) -> bool:
        entity.chat_flow.finished_flow.append(
            FlowEdgeMessage(
                type="answer",
                publish=True,
                edge_message_id=edge_message_id,
                consumed=False,
                user_id=chat.user_id
            )
        )
        _increment_iteration(chat=entity, answer=user_answer)
        return await _launch_transition(
            entity=entity,
            technical_id=technical_id,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            transition=process_entity_transition if process_entity_transition else transition
        )

    # last child entity always takes precedence
    # Recursive DFS that only unlocks on the root fallback
    async def traverse_and_process(
            entity: ChatEntity,
            technical_id: str,
            is_root: bool = False
    ) -> bool:
        # If locked and has children, try them first
        if entity.current_state.startswith(const.LOCKED_CHAT) and entity.child_entities:
            for child_id in reversed(entity.child_entities):
                child = await entity_service.get_item(
                    token=cyoda_auth_service,
                    entity_model=const.CHAT_MODEL_NAME,
                    entity_version=config.ENTITY_VERSION,
                    technical_id=child_id
                )

                # Recurse into further-locked nodes
                if child.current_state.startswith(const.LOCKED_CHAT) and child.child_entities:
                    if await traverse_and_process(child, child_id, False):
                        return True

                # If we find an unlocked child, process it and stop
                if not child.current_state.startswith(const.LOCKED_CHAT):
                    return await process_entity(child, child_id)

            # No unlocked descendants—only unlock if this is the root
            if is_root:
                entity.locked = False
                # launch a transition to clear the lock
                await _launch_transition(
                    entity=entity,
                    technical_id=technical_id,
                    entity_service=entity_service,
                    cyoda_auth_service=cyoda_auth_service,
                    transition=const.UNLOCK_CHAT_TRANSITION
                )
                return await process_entity(entity, technical_id)
            else:
                # intermediate locked node but nothing to do here
                return False
        elif entity.current_state.startswith(const.LOCKED_CHAT) and not entity.child_entities:
            entity.locked = False
            # launch a transition to clear the lock
            await _launch_transition(
                entity=entity,
                technical_id=technical_id,
                entity_service=entity_service,
                cyoda_auth_service=cyoda_auth_service,
                transition=const.UNLOCK_CHAT_TRANSITION
            )
            return await process_entity(entity, technical_id)
        # Otherwise (not locked or no children): process immediately
        return await process_entity(entity, technical_id)

    # Kick off with is_root=True so only chat itself can be unlocked
    transitioned = await traverse_and_process(chat, chat.technical_id, is_root=True)
    return edge_message_id, transitioned


async def add_answer_to_finished_flow(entity_service, answer: str, cyoda_auth_service, publish=True):
    flow_message_content = {
        "type": "answer",
        "answer": answer,
        "publish": publish
    }
    edge_message_id = await entity_service.add_item(token=cyoda_auth_service,
                                                    entity_model=const.FLOW_EDGE_MESSAGE_MODEL_NAME,
                                                    entity_version=config.ENTITY_VERSION,
                                                    entity=flow_message_content,
                                                    meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})

    return edge_message_id


async def get_user_message(message, user_file):
    if user_file:
        file_contents = read_file_content(user_file)
        message = f"{message}: {file_contents}" if message else file_contents
    return message


def _increment_iteration(chat, answer):
    pass
    # if answer == APPROVE:
    # pass
    # todo!
    # transition = chat.current_transition
    # chat.transitions_memory.get("current_iteration")[transition] = MAX_ITERATION + 1


async def _launch_transition(entity_service,
                             technical_id,
                             cyoda_auth_service,
                             entity=None,
                             transition=None):
    next_transitions = await entity_service.get_transitions(token=cyoda_auth_service,
                                                            meta={},
                                                            technical_id=technical_id)
    if not next_transitions:
        logger.exception(f"No transitions found technical_id={technical_id}")
        return False

    if transition and transition not in next_transitions:
        logger.exception(f"Sorry, no valid transitions found for transition {transition}")
        return False

    next_transition = transition if transition else next_transitions[0]

    if next_transition == const.MANUAL_RETRY_TRANSITION and const.ROLLBACK_TRANSITION in next_transitions:
        next_transition = const.ROLLBACK_TRANSITION
    elif next_transition == const.MANUAL_RETRY_TRANSITION and const.PROCESS_USER_INPUT_TRANSITION in next_transitions:
        next_transition = const.PROCESS_USER_INPUT_TRANSITION
    if not next_transition:
        logger.exception('Sorry, no valid transitions found')
        return False

    await entity_service.update_item(token=cyoda_auth_service,
                                     entity_model=const.CHAT_MODEL_NAME,
                                     entity_version=config.ENTITY_VERSION,
                                     technical_id=technical_id,
                                     entity=entity,
                                     meta={"update_transition": next_transition})
    return True


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
            entity_model=const.EDGE_MESSAGE_STORE_MODEL_NAME,
            entity_version=config.ENTITY_VERSION,
            technical_id=edge_id,
            meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE},
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
