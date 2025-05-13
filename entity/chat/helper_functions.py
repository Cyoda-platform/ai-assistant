import json
import logging
import os

from common.config.config import config
import common.config.const as const
from common.utils.chat_util_functions import add_answer_to_finished_flow
from common.utils.utils import current_timestamp
from entity.chat.chat import ChatEntity
from entity.model import SchedulerEntity, FlowEdgeMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

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
                                      edge_messages_store=None):

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
            "transitions_memory": {
                "conditions": {},
                "current_iteration": {},
                "max_iteration": {}
            }
        })
        if user_request:
            user_request_message_id = await add_answer_to_finished_flow(entity_service=entity_service,
                                                                        answer=user_request,
                                                                        cyoda_auth_service=self.cyoda_auth_service,
                                                                        publish=False)

            child_entity.chat_flow.finished_flow.append(FlowEdgeMessage(type="answer",
                                                                        publish=False,
                                                                        edge_message_id=user_request_message_id,
                                                                        consumed=False,
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
                                        scheduled_action: config.ScheduledAction = config.ScheduledAction.SCHEDULE_ENTITIES_FLOW):

        child_entity: SchedulerEntity = SchedulerEntity.model_validate({
            "user_id": "system",
            "workflow_name": const.ModelName.SCHEDULER_ENTITY.value,
            "awaited_entity_ids": awaited_entity_ids,
            "triggered_entity_id": triggered_entity_id,
            "scheduled_action": scheduled_action.value
        })

        child_technical_id = await entity_service.add_item(token=self.cyoda_auth_service,
                                                           entity_model=const.ModelName.SCHEDULER_ENTITY.value,
                                                           entity_version=config.ENTITY_VERSION,
                                                           entity=child_entity)

        return child_technical_id