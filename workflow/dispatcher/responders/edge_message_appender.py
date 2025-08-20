"""EdgeMessageAppender for handling edge messages in workflow flow."""

import json
import logging
from typing import List
from entity.chat.chat import AgenticFlowEntity
from entity.model import FlowEdgeMessage
from common.config.config import config as env_config
import common.config.const as const
from common.utils.utils import get_current_timestamp_num, _post_process_response
from workflow.dispatcher.events.processing_context import ProcessingContext
from workflow.dispatcher.events.services import Services
from workflow.dispatcher.actions.action import Action

logger = logging.getLogger(__name__)


class EdgeMessageAppender:
    """Handles appending edge messages to workflow flow."""
    
    async def append(self, ctx: ProcessingContext, action: Action, response: str) -> None:
        """Append edge messages for the action and response."""
        if not isinstance(ctx.event.entity, AgenticFlowEntity):
            return
        
        entity = ctx.event.entity
        config = action.config
        finished_flow = entity.chat_flow.finished_flow
        
        # Create initial edge message
        message = FlowEdgeMessage(
            type=config.get("type"),
            approve=config.get('approve'),
            publish=config.get('publish'),
            message=config.get(config.get("type")),
            last_modified=get_current_timestamp_num()
        )
        await self._add_edge_message(
            message=message, 
            flow=finished_flow, 
            user_id=entity.user_id,
            services=ctx.services
        )
        
        config_type = config.get("type")
        if config_type in ("function", "prompt", "agent"):
            if response and response != "None":
                if isinstance(response, str) and response.strip().startswith('{\"type\": \"ui_function\"'):
                    response_data = json.loads(response)
                    notification = FlowEdgeMessage(
                        publish=config.get("publish", False),
                        message=_post_process_response(response=f"{response_data}", config=config),
                        approve=config.get("approve", False),
                        type=const.UI_FUNCTION_PREFIX
                    )
                else:
                    notification = FlowEdgeMessage(
                        publish=config.get("publish", False),
                        message=_post_process_response(response=f"{response}", config=config),
                        approve=config.get("approve", False),
                        type="question"
                    )
                await self._add_edge_message(
                    message=notification,
                    flow=finished_flow,
                    user_id=entity.user_id,
                    services=ctx.services
                )
    
    async def _add_edge_message(self, message: FlowEdgeMessage, flow: List[FlowEdgeMessage], 
                               user_id: str, services: Services) -> FlowEdgeMessage:
        """Add an edge message to the flow."""
        edge_message_id = await services.entity_service.add_item(
            token=services.cyoda_auth_service,
            entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
            entity_version=env_config.ENTITY_VERSION,
            entity=message,
            meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
        )

        flow_edge_message = FlowEdgeMessage(
            type=message.type,
            publish=message.publish,
            edge_message_id=edge_message_id,
            last_modified=message.last_modified,
            user_id=user_id
        )
        flow.append(flow_edge_message)
        return flow_edge_message
