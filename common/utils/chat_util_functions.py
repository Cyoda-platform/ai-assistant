import logging
import asyncio
import common.config.const as const
from typing import Tuple

from common.config.config import config
from common.utils.file_reader import read_file_content
from common.utils.utils import get_current_timestamp_num
from entity.chat.chat import ChatEntity
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
    edge_message_id, last_modified = await add_answer_to_finished_flow(
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
                last_modified=last_modified,
                consumed=transition==const.TransitionKey.MANUAL_APPROVE.value,
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
    # IMPROVED VERSION: Handles race conditions and service failures
    async def traverse_and_process(
            entity: ChatEntity,
            technical_id: str,
            is_root: bool = False,
            max_retries: int = 3,
            retry_delay: float = 0.1
    ) -> bool:
        # If locked and has children, try them first
        if entity.current_state.startswith(const.TransitionKey.LOCKED_CHAT.value) and entity.child_entities:
            # Create a stable copy of child_entities to avoid concurrent modification issues
            child_entities_copy = list(entity.child_entities)

            # Log the traversal for debugging
            logger.debug(f"Traversing entity {technical_id} with {len(child_entities_copy)} children")

            for child_id in reversed(child_entities_copy):
                # Retry mechanism for entity retrieval to handle race conditions
                child = None
                last_exception = None

                for attempt in range(max_retries):
                    try:
                        child = await entity_service.get_item(
                            token=cyoda_auth_service,
                            entity_model=const.ModelName.CHAT_ENTITY.value,
                            entity_version=config.ENTITY_VERSION,
                            technical_id=child_id
                        )

                        # Validate that we got a valid entity with required attributes
                        if child and hasattr(child, 'current_state') and child.current_state is not None:
                            logger.debug(f"Successfully retrieved child {child_id} with state: {child.current_state}")
                            break
                        else:
                            # Log warning and retry
                            logger.warning(f"Retrieved invalid child entity {child_id} (missing current_state), attempt {attempt + 1}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay)

                    except Exception as e:
                        last_exception = e
                        logger.warning(f"Failed to retrieve child entity {child_id}, attempt {attempt + 1}: {e}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                        else:
                            # Log final failure
                            logger.error(f"Failed to retrieve child entity {child_id} after {max_retries} attempts: {e}")

                # Skip if we couldn't retrieve the child entity
                if not child or not hasattr(child, 'current_state') or child.current_state is None:
                    logger.warning(f"Skipping child entity {child_id} - could not retrieve valid entity")
                    continue

                # Double-check the current state after retrieval (race condition protection)
                current_state = getattr(child, 'current_state', '')
                child_entities = getattr(child, 'child_entities', [])

                logger.debug(f"Processing child {child_id} with state: {current_state}, has children: {bool(child_entities)}")

                # Recurse into further-locked nodes
                if current_state.startswith(const.TransitionKey.LOCKED_CHAT.value) and child_entities:
                    logger.debug(f"Recursing into locked child {child_id}")
                    if await traverse_and_process(child, child_id, False, max_retries, retry_delay):
                        return True

                # If we find an unlocked child, process it and stop
                if not current_state.startswith(const.TransitionKey.LOCKED_CHAT.value):
                    logger.info(f"Found unlocked child entity {child_id} with state: {current_state}")
                    processed = await process_entity(child, child_id)
                    retry_count = 3
                    while not processed and retry_count > 0:
                        logger.exception(f"Failed to process entity {child_id}, retrying...")
                        processed = await process_entity(child, child_id)
                        retry_count -= 1
                    if not processed:
                        raise Exception(f"Failed to process entity {child_id} after {max_retries} attempts")
                    return True

            # No unlocked descendants—only unlock if this is the root
            if is_root:
                logger.info(f"No unlocked descendants found, unlocking root entity {technical_id}")
                entity.locked = False
                # launch a transition to clear the lock
                await _launch_transition(
                    entity=entity,
                    technical_id=technical_id,
                    entity_service=entity_service,
                    cyoda_auth_service=cyoda_auth_service,
                    transition=const.TransitionKey.UNLOCK_CHAT.value
                )
                return await process_entity(entity, technical_id)
            else:
                # intermediate locked node but nothing to do here
                logger.debug(f"Intermediate locked node {technical_id} - no action taken")
                return False

        elif entity.current_state.startswith(const.TransitionKey.LOCKED_CHAT.value) and not entity.child_entities:
            logger.info(f"Unlocking leaf entity {technical_id}")
            entity.locked = False
            # launch a transition to clear the lock
            await _launch_transition(
                entity=entity,
                technical_id=technical_id,
                entity_service=entity_service,
                cyoda_auth_service=cyoda_auth_service,
                transition=const.TransitionKey.UNLOCK_CHAT.value
            )
            return await process_entity(entity, technical_id)

        # Otherwise (not locked or no children): process immediately
        logger.info(f"Processing unlocked entity {technical_id} with state: {entity.current_state}")
        return await process_entity(entity, technical_id)

    # Kick off with is_root=True so only chat itself can be unlocked
    transitioned = await traverse_and_process(chat, chat.technical_id, is_root=True)
    return edge_message_id, transitioned


async def add_answer_to_finished_flow(entity_service, answer: str, cyoda_auth_service, publish=True):
    last_modified = get_current_timestamp_num()
    flow_message_content = {
        "type": "answer",
        "message": answer,
        "publish": publish,
        "last_modified": last_modified
    }
    edge_message_id = await entity_service.add_item(token=cyoda_auth_service,
                                                    entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                                                    entity_version=config.ENTITY_VERSION,
                                                    entity=FlowEdgeMessage.model_validate(flow_message_content),
                                                    meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})

    return edge_message_id, last_modified


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


async def _launch_transition(
    entity_service,
    technical_id: str,
    cyoda_auth_service,
    entity=None,
    transition: str = None
) -> bool:
    """
    Launch a workflow transition for a chat entity.

    Args:
        entity_service: Service for entity operations
        technical_id: Unique identifier for the entity
        cyoda_auth_service: Authentication service for Cyoda
        entity: Optional entity data
        transition: Optional specific transition to execute

    Returns:
        bool: True if transition was successful, False otherwise
    """
    try:
        next_transitions = await entity_service.get_transitions(
            token=cyoda_auth_service,
            meta={},
            technical_id=technical_id
        )

        if not next_transitions:
            logger.error(f"No transitions found for technical_id={technical_id}")
            return False

        selected_transition = _select_transition(
            requested_transition=transition,
            available_transitions=next_transitions
        )

        if not selected_transition:
            logger.error(f"No valid transition selected for technical_id={technical_id}")
            return False

        await entity_service.update_item(
            token=cyoda_auth_service,
            entity_model=const.ModelName.CHAT_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            technical_id=technical_id,
            entity=entity,
            meta={"update_transition": selected_transition}
        )

        logger.info(f"Successfully launched transition '{selected_transition}' for technical_id={technical_id}")
        return True

    except Exception as e:
        logger.exception(f"Failed to launch transition for technical_id={technical_id}: {e}")
        return False


def _select_transition(requested_transition: str, available_transitions: list) -> str:
    """
    Select the appropriate transition based on request and availability.

    Args:
        requested_transition: The transition requested by the caller
        available_transitions: List of available transitions

    Returns:
        str: The selected transition name, or empty string if none valid
    """
    if requested_transition and requested_transition not in available_transitions:
        logger.error(f"Requested transition '{requested_transition}' not in available transitions: {available_transitions}")
        return ""

    selected_transition = requested_transition or available_transitions[0]

    # Apply business rule: prefer rollback over manual retry
    if (selected_transition == const.TransitionKey.MANUAL_RETRY.value and
        const.TransitionKey.ROLLBACK.value in available_transitions):
        selected_transition = const.TransitionKey.ROLLBACK.value
        logger.info("Switching from manual_retry to rollback transition")

    return selected_transition


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
            entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
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
