"""Services container for the event processing system."""

from workflow.dispatcher.interfaces import MemoryManager, DefaultMemoryManager


class Services:
    """Container for all services needed by the event processing system."""

    def __init__(self, method_registry, ai_agent_handler, memory_manager,
                 file_handler, message_processor, user_service, entity_service,
                 cyoda_auth_service, config_builder):
        self.method_registry = method_registry
        self.ai_agent_handler = ai_agent_handler
        self.memory_manager = memory_manager
        self.file_handler = file_handler
        self.message_processor = message_processor
        self.user_service = user_service
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
        self.config_builder = config_builder

        # Wrap memory manager to implement interface
        self._memory_manager_interface = DefaultMemoryManager(memory_manager)

    def get_memory_manager(self) -> MemoryManager:
        """Get memory manager interface"""
        return self._memory_manager_interface

    def set_memory_manager(self, manager: MemoryManager) -> None:
        """Set custom memory manager"""
        self._memory_manager_interface = manager
