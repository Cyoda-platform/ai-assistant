import json
import logging
import os
from typing import Dict, Any

import aiofiles
from common.config.config import config
import common.config.const as const
from common.utils.chat_util_functions import add_answer_to_finished_flow
from common.utils.utils import current_timestamp, get_current_timestamp_num, _save_file
from entity.chat.chat import ChatEntity
from entity.model import SchedulerEntity, FlowEdgeMessage

logger = logging.getLogger(__name__)


class WorkflowHelperService:
    def __init__(self, cyoda_auth_service, mock=False):
        self.mock = mock
        self.cyoda_auth_service = cyoda_auth_service

    if config.MOCK_AI == "true":
        # generate_mock_data()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.path.dirname(current_dir)
        # Build the file path
        mock_external_data_path = os.path.join(current_dir, 'data', "mock_external_data.json")
        try:
            with open(mock_external_data_path, 'r') as file:
                data = file.read()
        except Exception as e:
            logger.error(f"Failed to read JSON file {mock_external_data_path}: {e}")
            raise
        json_mock_data = json.loads(data)

    # =============================
    async def launch_agentic_workflow(self,
                                      entity_service,
                                      technical_id,
                                      entity,
                                      entity_model,
                                      workflow_name,
                                      user_request=None,
                                      workflow_cache=None,
                                      edge_messages_store=None,
                                      resume_transition=None):

        child_entity: ChatEntity = ChatEntity.model_validate({
            "user_id": entity.user_id,
            "workflow_name": workflow_name,
            "chat_id": "",
            "parent_id": technical_id,
            "date": current_timestamp(),
            "questions_queue_id": entity.questions_queue_id,
            "memory_id": entity.memory_id,
            "chat_flow": {"current_flow": [], "finished_flow": []},
            "current_transition": "",
            "current_state": "",
            "workflow_cache": workflow_cache,
            "edge_messages_store": edge_messages_store,
            "resume_transition": resume_transition,
            "transitions_memory": {
                "conditions": {},
                "current_iteration": {},
                "max_iteration": {}
            }
        })
        if user_request:
            user_request_message_id, last_modified = await add_answer_to_finished_flow(entity_service=entity_service,
                                                                                       answer=user_request,
                                                                                       cyoda_auth_service=self.cyoda_auth_service,
                                                                                       publish=False)

            child_entity.chat_flow.finished_flow.append(FlowEdgeMessage(type="answer",
                                                                        publish=False,
                                                                        edge_message_id=user_request_message_id,
                                                                        consumed=False,
                                                                        last_modified=last_modified,
                                                                        user_id=entity.user_id))

        child_technical_id = await entity_service.add_item(token=self.cyoda_auth_service,
                                                           entity_model=entity_model,
                                                           entity_version=config.ENTITY_VERSION,
                                                           entity=child_entity)
        # lock parent chat
        entity.locked = True
        entity.child_entities.append(child_technical_id)
        return child_technical_id

    async def launch_scheduled_workflow(self,
                                        entity_service,
                                        awaited_entity_ids,
                                        triggered_entity_id,
                                        triggered_entity_next_transition: str = None,
                                        scheduled_action: config.ScheduledAction = config.ScheduledAction.SCHEDULE_ENTITIES_FLOW,
                                        ):

        child_entity: SchedulerEntity = SchedulerEntity(
            user_id="system",
            workflow_name=const.ModelName.SCHEDULER_ENTITY.value,
            awaited_entity_ids=awaited_entity_ids,
            triggered_entity_id=triggered_entity_id,
            scheduled_action=scheduled_action.value,
            triggered_entity_next_transition=triggered_entity_next_transition,
            last_modified=get_current_timestamp_num()
        )

        child_technical_id = await entity_service.add_item(token=self.cyoda_auth_service,
                                                           entity_model=const.ModelName.SCHEDULER_ENTITY.value,
                                                           entity_version=config.ENTITY_VERSION,
                                                           entity=child_entity)

        return child_technical_id

    async def order_states_in_fsm(self, fsm):
        states = fsm["states"]
        initial_state = fsm["initial_state"]
        ordered_state_names = []
        visited = set()

        def dfs(state_name):
            if state_name in visited or state_name not in states:
                return
            visited.add(state_name)
            ordered_state_names.append(state_name)
            transitions = states[state_name].get("transitions", {})
            for transition in transitions.values():
                next_state = transition.get("next")
                if next_state:
                    dfs(next_state)

        dfs(initial_state)

        # Add any orphan/unreachable states at the end (to preserve original input fully)
        for state_name in states:
            if state_name not in visited:
                ordered_state_names.append(state_name)

        # Reconstruct FSM with ordered states
        ordered_states = {name: states[name] for name in ordered_state_names}
        ordered_fsm = {
            **fsm,
            "states": ordered_states
        }

        return ordered_fsm

    async def read_json(self, path: str) -> Dict:
        """Helper to read JSON from disk asynchronously."""
        async with aiofiles.open(path, mode="r") as f:
            text = await f.read()
        return json.loads(text)

    async def persist_json(
            self,
            path_or_item: str,
            data: Any,
            git_branch_id: str,
            repository_name: str,
    ) -> None:
        """
        Serialize `data` to JSON and save via our common `_save_file` helper.
        `path_or_item` may be either an existing file path or a target filename.
        """
        payload = json.dumps(
            data,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        await _save_file(
            _data=payload,
            item=path_or_item,
            git_branch_id=git_branch_id,
            repository_name=repository_name,
        )

