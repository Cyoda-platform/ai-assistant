"""EventDispatcher - main event dispatcher that coordinates all components."""

import asyncio
import json
import logging
from typing import Tuple, Any
from entity.chat.chat import AgenticFlowEntity
from entity.model import WorkflowEntity
from common.utils.utils import get_current_timestamp_num
from workflow.dispatcher.events import WorkflowEvent, ProcessingContext, Services
from workflow.dispatcher.resolvers import ActionResolver
from workflow.dispatcher.processors import ProcessorSelector
from workflow.dispatcher.responders import OutputWriter, EdgeMessageAppender, Responder

logger = logging.getLogger(__name__)


class EventDispatcher:
    """
    Main event dispatcher that coordinates all components according to the class diagram.
    Replaces the original EventProcessor with a more modular design.
    """
    
    def __init__(self, method_registry, ai_agent_handler, memory_manager,
                 file_handler, message_processor, user_service, entity_service, 
                 cyoda_auth_service, config_builder):
        """Initialize the event dispatcher with all required services."""
        self.services = Services(
            method_registry, ai_agent_handler, memory_manager, file_handler,
            message_processor, user_service, entity_service, cyoda_auth_service,
            config_builder
        )
        
        self.action_resolver = ActionResolver()
        self.processor_selector = ProcessorSelector()
        
        # Initialize responder components
        self._write_output_lock = asyncio.Lock()
        self.output_writer = OutputWriter(self._write_output_lock)
        self.edge_message_appender = EdgeMessageAppender()
        self.responder = Responder(self.output_writer, self.edge_message_appender)
    
    async def process(self, event: WorkflowEvent) -> Tuple[WorkflowEntity, Any]:
        """
        Process a workflow event using the modular architecture.
        
        Args:
            event: Workflow event to process
            
        Returns:
            Tuple of (updated_entity, response)
        """
        ctx = ProcessingContext(event, self.services)
        
        try:
            # Get user account information
            event.entity.user_id = await self.services.user_service.get_entity_account(
                user_id=event.entity.user_id
            )
            
            # Store child entities size for new entity tracking
            if isinstance(event.entity, AgenticFlowEntity):
                ctx.child_entities_size_before = len(event.entity.child_entities)
            
            # Build config if needed
            await self._build_config(ctx)
            
            # Resolve action
            action = self.action_resolver.resolve(ctx)
            
            # Select and execute processor
            processor = self.processor_selector.select(action)
            ctx.response = await processor.execute(ctx, action)
            
            # Finalize response
            await self.responder.finalize(ctx, action, ctx.response)
            
        except Exception as e:
            event.entity.failed = True
            event.entity.last_modified = get_current_timestamp_num()
            event.entity.error = f"Error: {e}"
            logger.exception(f"Exception occurred while processing event: {e}")
        
        logger.info(f"{event.processor_name}: {ctx.response}")
        event.entity.last_modified = get_current_timestamp_num()
        return event.entity, ctx.response
    
    async def _build_config(self, ctx: ProcessingContext) -> None:
        """Build configuration for the processing context."""
        processor_name = ctx.event.processor_name
        payload = ctx.event.payload
        
        # Skip config building for direct methods
        if "Processor." not in processor_name and processor_name != "process_event":
            return
        
        try:
            if processor_name == "process_event" and payload.get('parameters', {}).get('context'):
                ctx.config = json.loads(payload['parameters']['context'])
            else:
                ctx.config = await self.services.config_builder.build_config(processor_name)
        except (FileNotFoundError, ValueError) as config_error:
            logger.warning(f"Config build failed for {processor_name}: {config_error}. Will use direct method execution.")
            ctx.config = None
