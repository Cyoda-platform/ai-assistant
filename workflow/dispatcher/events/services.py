"""Services container for the event processing system."""


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
