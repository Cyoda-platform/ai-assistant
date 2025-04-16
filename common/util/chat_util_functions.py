from common.config.config import ENTITY_VERSION, CYODA_ENTITY_TYPE_EDGE_MESSAGE
from common.config.conts import LOCKED_CHAT, CHAT_MODEL_NAME, FLOW_EDGE_MESSAGE_MODEL_NAME
from common.repository.cyoda.cyoda_repository import cyoda_token
from common.util.file_reader import read_file_content
from entity.chat.model.chat import ChatEntity
from entity.model.model import FlowEdgeMessage


async def trigger_manual_transition(entity_service, chat: ChatEntity, answer, user_file=None, request=None):
    user_answer = await get_user_message(request = request, message=answer, user_file=user_file) if user_file else answer

    # Helper to process a chat entity: add answer, increment iteration, and launch transition.
    async def process_entity(entity: ChatEntity, technical_id: str):
        await add_answer_to_finished_flow(entity_service=entity_service, answer=user_answer, chat=entity)
        _increment_iteration(chat=entity, answer=user_answer)
        await _launch_transition(entity=entity, technical_id=technical_id, entity_service=entity_service)

    # If the chat is locked, try processing its child entities.
    if chat.child_entities and chat.current_state == LOCKED_CHAT:
        has_active_child = False

        # Iterate through child entities in reverse order.
        for child_id in reversed(chat.child_entities):
            child_entity = await entity_service.get_item(
                token=cyoda_token,
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
            await _launch_transition(entity=chat, technical_id=chat.technical_id, entity_service=entity_service)

            await process_entity(entity=chat, technical_id=chat.technical_id)
    else:
        # If the chat is not locked, process it directly.
        await process_entity(chat, chat.technical_id)


async def add_answer_to_finished_flow(entity_service, answer: str, chat: ChatEntity):
    finished_flow = chat.chat_flow.finished_flow
    flow_message_content = {
        "type": "answer",
        "answer": answer,
        "publish": True
    }
    edge_message_id = await entity_service.add_item(token=cyoda_token,
                                                    entity_model=FLOW_EDGE_MESSAGE_MODEL_NAME,
                                                    entity_version=ENTITY_VERSION,
                                                    entity=flow_message_content,
                                                    meta={"type": CYODA_ENTITY_TYPE_EDGE_MESSAGE})
    finished_flow.append(FlowEdgeMessage(type="answer",
                                         publish=True,
                                         edge_message_id=edge_message_id,
                                         consumed=False,
                                         user_id=chat.user_id))


async def get_user_message(request, message, user_file):
    if user_file:
        file = (await request.files).get('file')
        if file:
            file_contents = read_file_content(file)
            message = f"{message}: {file_contents}" if message else file_contents
    return message


def _increment_iteration(chat, answer):
    pass
    #if answer == APPROVE:
        #pass
        # todo!
        # transition = chat.current_transition
        # chat.transitions_memory.get("current_iteration")[transition] = MAX_ITERATION + 1


async def _launch_transition(entity_service, technical_id, entity=None):
    next_transitions = await entity_service.get_transitions(token=cyoda_token,
                                                            meta={},
                                                            technical_id=technical_id)
    # todo!!!
    next_transition = next_transitions[0]
    await entity_service.update_item(token=cyoda_token,
                                     entity_model=CHAT_MODEL_NAME,
                                     entity_version=ENTITY_VERSION,
                                     technical_id=technical_id,
                                     entity=entity,
                                     meta={"update_transition": next_transition})


# async def _trigger_manual_transition(chat, technical_id):
    # if fsm_implementation == FSM_LOCAL:
    #     fsm = await load_fsm()
    #     current_state = chat.current_state
    #     state_info = fsm["states"].get(current_state, {})
    #     manual_events = [
    #         event for event, transition in state_info.get("transitions", {}).items()
    #         if transition.get("manual", False)
    #     ]
    #
    #     if manual_events:
    #         asyncio.create_task(flow_processor.trigger_manual_transition(
    #             current_state=current_state,
    #             event=manual_events[0],
    #             entity=chat,
    #             fsm=fsm,
    #             technical_id=technical_id
    #         ))
    # else:

