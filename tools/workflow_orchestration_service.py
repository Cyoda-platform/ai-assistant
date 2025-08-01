"""
Workflow Orchestration Service.

This service contains the essential workflow orchestration logic that was previously
in entity/chat/helper_functions.py. It handles launching workflows, creating child
entities, and managing workflow state.
"""

import json
import logging
import os
from typing import Dict, Any, Optional

import aiofiles
from common.config.config import config
import common.config.const as const
from common.utils.chat_util_functions import add_answer_to_finished_flow
from common.utils.utils import current_timestamp, get_current_timestamp_num, _save_file
from entity.chat.chat import ChatEntity
from entity.model import SchedulerEntity, FlowEdgeMessage
from tools.base_service import BaseWorkflowService

logger = logging.getLogger(__name__)


class WorkflowOrchestrationService(BaseWorkflowService):
    """
    Service for orchestrating workflow execution and entity management.
    
    This service handles:
    - Launching agentic workflows
    - Creating child entities
    - Managing workflow state transitions
    - Scheduling workflows
    - JSON persistence operations
    """

    def __init__(self, workflow_helper_service, entity_service, cyoda_auth_service,
                 workflow_converter_service, scheduler_service, data_service,
                 dataset, mock=False):
        """Initialize the workflow orchestration service."""
        super().__init__(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )
        
        # Load mock data if needed
        if config.MOCK_AI == "true":
            self._load_mock_data()

    def _load_mock_data(self):
        """Load mock external data for testing."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            current_dir = os.path.dirname(current_dir)
            mock_external_data_path = os.path.join(current_dir, 'data', "mock_external_data.json")
            
            with open(mock_external_data_path, 'r') as file:
                data = file.read()
            self.json_mock_data = json.loads(data)
        except Exception as e:
            logger.error(f"Failed to read JSON file {mock_external_data_path}: {e}")
            self.json_mock_data = {}

    async def launch_agentic_workflow(self,
                                      technical_id: str,
                                      entity: Any,
                                      entity_model: str,
                                      workflow_name: str,
                                      user_request: Optional[str] = None,
                                      workflow_cache: Optional[Dict[str, Any]] = None,
                                      edge_messages_store: Optional[Dict[str, Any]] = None,
                                      resume_transition: Optional[str] = None) -> str:
        """
        Launch an agentic workflow by creating a child entity.
        
        Args:
            technical_id: Parent entity technical ID
            entity: Parent entity object
            entity_model: Entity model name
            workflow_name: Name of workflow to launch
            user_request: Optional user request to include
            workflow_cache: Optional workflow cache data
            edge_messages_store: Optional edge messages store
            resume_transition: Optional transition to resume from
            
        Returns:
            Technical ID of created child entity
        """
        # Create child entity
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
            "workflow_cache": workflow_cache or {},
            "edge_messages_store": edge_messages_store or {},
            "resume_transition": resume_transition,
            "transitions_memory": {
                "conditions": {},
                "current_iteration": {},
                "max_iteration": {}
            }
        })
        
        # Add user request if provided
        if user_request:
            user_request_message_id, last_modified = await add_answer_to_finished_flow(
                entity_service=self.entity_service,
                answer=user_request,
                cyoda_auth_service=self.cyoda_auth_service,
                publish=False
            )

            child_entity.chat_flow.finished_flow.append(FlowEdgeMessage(
                type="answer",
                publish=False,
                edge_message_id=user_request_message_id,
                consumed=False,
                last_modified=last_modified,
                user_id=entity.user_id
            ))

        # Create child entity in database
        child_technical_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=entity_model,
            entity_version=config.ENTITY_VERSION,
            entity=child_entity
        )
        
        # Lock parent chat and add child reference
        entity.locked = True
        entity.child_entities.append(child_technical_id)
        
        return child_technical_id

    async def launch_scheduled_workflow(self,
                                        awaited_entity_ids: list,
                                        triggered_entity_id: str,
                                        triggered_entity_next_transition: Optional[str] = None,
                                        scheduled_action: config.ScheduledAction = config.ScheduledAction.SCHEDULE_ENTITIES_FLOW) -> str:
        """
        Launch a scheduled workflow by creating a scheduler entity.
        
        Args:
            awaited_entity_ids: List of entity IDs to wait for
            triggered_entity_id: Entity ID that triggered the schedule
            triggered_entity_next_transition: Next transition for triggered entity
            scheduled_action: Type of scheduled action
            
        Returns:
            Technical ID of created scheduler entity
        """
        child_entity: SchedulerEntity = SchedulerEntity(
            user_id="system",
            workflow_name=const.ModelName.SCHEDULER_ENTITY.value,
            awaited_entity_ids=awaited_entity_ids,
            triggered_entity_id=triggered_entity_id,
            scheduled_action=scheduled_action.value,
            triggered_entity_next_transition=triggered_entity_next_transition,
            last_modified=get_current_timestamp_num()
        )

        child_technical_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.SCHEDULER_ENTITY.value,
            entity_version=config.ENTITY_VERSION,
            entity=child_entity
        )

        return child_technical_id

    async def order_states_in_fsm(self, fsm: Dict[str, Any]) -> Dict[str, Any]:
        """
        Order states in a finite state machine based on transitions.
        
        Args:
            fsm: Finite state machine definition
            
        Returns:
            FSM with ordered states
        """
        states = fsm["states"]
        initial_state = fsm["initialState"]
        ordered_state_names = []
        visited = set()

        def dfs(state_name):
            if state_name in visited or state_name not in states:
                return
            visited.add(state_name)
            ordered_state_names.append(state_name)
            transitions = states[state_name].get("transitions", [])
            for transition in transitions:
                next_state = transition.get("next")
                if next_state:
                    dfs(next_state)

        dfs(initial_state)

        # Add any orphan/unreachable states at the end
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

    async def read_json(self, path: str) -> Dict[str, Any]:
        """
        Read JSON from disk asynchronously.
        
        Args:
            path: File path to read
            
        Returns:
            Parsed JSON data
        """
        async with aiofiles.open(path, mode="r") as f:
            text = await f.read()
        return json.loads(text)

    async def persist_json(self,
                          path_or_item: str,
                          data: Any,
                          git_branch_id: str,
                          repository_name: str) -> None:
        """
        Serialize data to JSON and save via common save helper.
        
        Args:
            path_or_item: File path or target filename
            data: Data to serialize
            git_branch_id: Git branch ID
            repository_name: Repository name
        """
        payload = json.dumps(data, indent=2)
        await _save_file(
            _data=payload,
            item=path_or_item,
            git_branch_id=git_branch_id,
            repository_name=repository_name,
        )


# Backward compatibility alias
WorkflowHelperService = WorkflowOrchestrationService
