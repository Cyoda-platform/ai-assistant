"""MessageProcessor for notification/message actions."""

import logging
from typing import Dict, Any
from entity.chat.chat import AgenticFlowEntity
from common.config.config import config as env_config
from workflow.dispatcher.events.processing_context import ProcessingContext
from workflow.dispatcher.actions.action import Action
from .processor import Processor

logger = logging.getLogger(__name__)


class MessageProcessor(Processor):
    """Processor for notification/message actions."""
    
    async def execute(self, ctx: ProcessingContext, action: Action) -> str:
        """Execute message processing."""
        if not isinstance(ctx.event.entity, AgenticFlowEntity):
            return "Error: MessageProcessor requires AgenticFlowEntity"
        
        config_type = action.config.get("type")
        message = action.config.get(config_type, "")

        # Format message with entity cache
        formatted_message = self._format_message(
            message=message, 
            cache=ctx.event.entity.workflow_cache
        )

        # Update config with formatted message (important for downstream processing)
        action.config[config_type] = formatted_message

        # Store in memory if needed
        memory_tags = action.config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])
        if memory_tags:
            await ctx.services.memory_manager.append_to_ai_memory(
                entity=ctx.event.entity, content=formatted_message, memory_tags=memory_tags
            )

        return formatted_message
    
    def _format_message(self, message: str, cache: Dict[str, Any]) -> str:
        """Format message with cache values."""
        try:
            return message.format(**cache)
        except Exception as e:
            logger.exception(f"Error formatting message: {e}")
            return message
