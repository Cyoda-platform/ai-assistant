"""
EventProcessor module - provides backward compatibility wrapper for the new modular architecture.

This module maintains the original EventProcessor interface while delegating to the new
modular components organized in separate directories.
"""

import logging
from typing import Tuple, Any, List
from entity.model import WorkflowEntity, FlowEdgeMessage
from workflow.dispatcher.events import WorkflowEvent
from workflow.dispatcher.dispatchers import EventDispatcher

logger = logging.getLogger(__name__)


class EventProcessor:
    """
    Backward compatibility wrapper for the original EventProcessor interface.
    Delegates to the new EventDispatcher while maintaining the same API.
    """

    def __init__(self, method_registry, ai_agent_handler, memory_manager,
                 file_handler, message_processor, user_service, entity_service,
                 cyoda_auth_service, config_builder):
        """Initialize with backward compatibility."""
        self.dispatcher = EventDispatcher(
            method_registry, ai_agent_handler, memory_manager, file_handler,
            message_processor, user_service, entity_service, cyoda_auth_service,
            config_builder
        )

        # Expose services for backward compatibility
        self.method_registry = method_registry
        self.ai_agent_handler = ai_agent_handler
        self.memory_manager = memory_manager
        self.file_handler = file_handler
        self.message_processor = message_processor
        self.user_service = user_service
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
        self.config_builder = config_builder
        self._write_output_lock = self.dispatcher._write_output_lock

    async def process_event(self, entity: WorkflowEntity, processor_name: str, payload: Any,
                           technical_id: str) -> Tuple[WorkflowEntity, Any]:
        """
        Process a workflow event - backward compatibility method.

        Args:
            entity: Workflow entity
            processor_name: Processor name
            payload: Event payload
            technical_id: Technical identifier

        Returns:
            Tuple of (updated_entity, response)
        """
        event = WorkflowEvent(entity, processor_name, payload, technical_id)
        return await self.dispatcher.process(event)

    async def add_edge_message(self, message: FlowEdgeMessage, flow: List[FlowEdgeMessage],
                              user_id: str) -> FlowEdgeMessage:
        """Add an edge message to the flow - backward compatibility method."""
        return await self.dispatcher.edge_message_appender._add_edge_message(
            message, flow, user_id, self.dispatcher.services
        )

