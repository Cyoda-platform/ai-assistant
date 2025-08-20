"""Responder for handling response finalization and coordination."""

from entity.chat.chat import AgenticFlowEntity
from entity.model import FlowEdgeMessage
from common.utils.utils import get_current_timestamp_num
from workflow.dispatcher.events.processing_context import ProcessingContext
from workflow.dispatcher.actions.action import Action
from .output_writer import OutputWriter
from .edge_message_appender import EdgeMessageAppender


class Responder:
    """Handles response finalization and coordination."""
    
    def __init__(self, output_writer: OutputWriter, edge_message_appender: EdgeMessageAppender):
        self.output_writer = output_writer
        self.edge_message_appender = edge_message_appender
    
    async def finalize(self, ctx: ProcessingContext, action: Action, response: str) -> None:
        """Finalize response by handling outputs and edge messages."""
        if isinstance(ctx.event.entity, AgenticFlowEntity):
            # Handle new entities
            child_entities_size_before = getattr(ctx, 'child_entities_size_before', 0)
            new_entities = ctx.event.entity.child_entities[child_entities_size_before:] if child_entities_size_before < len(
                ctx.event.entity.child_entities) else []
            
            if new_entities:
                message = FlowEdgeMessage(
                    type="child_entities",
                    message=new_entities,
                    last_modified=get_current_timestamp_num()
                )
                await self.edge_message_appender._add_edge_message(
                    message=message, 
                    flow=ctx.event.entity.chat_flow.finished_flow,
                    user_id=ctx.event.entity.user_id,
                    services=ctx.services
                )
            
            # Append edge messages
            await self.edge_message_appender.append(ctx, action, response)
            
            # Write outputs
            await self.output_writer.write(ctx, response)
