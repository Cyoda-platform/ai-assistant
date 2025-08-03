import logging
from typing import Dict, Any, Tuple

from entity.model import WorkflowEntity
from workflow.config_builder import ConfigBuilder
from workflow.dispatcher.method_registry import MethodRegistry
from workflow.dispatcher.memory_manager import MemoryManager
from workflow.dispatcher.ai_agent_handler import AIAgentHandler
from workflow.dispatcher.file_handler import FileHandler
from workflow.dispatcher.message_processor import MessageProcessor
from workflow.dispatcher.event_processor import EventProcessor

logger = logging.getLogger(__name__)


class WorkflowDispatcher:
    """
    Refactored WorkflowDispatcher with separated concerns.
    
    This is the main orchestrator that coordinates between different specialized components:
    - MethodRegistry: Handles method collection and dispatch
    - MemoryManager: Manages chat memory and AI messages
    - AIAgentHandler: Handles AI agent interactions
    - FileHandler: Manages file operations
    - MessageProcessor: Processes and formats messages
    - EventProcessor: Coordinates event processing logic
    """
    
    def __init__(self, cls, cls_instance, ai_agent, entity_service, 
                 cyoda_auth_service, user_service, mock=False):
        """
        Initialize the workflow dispatcher with all its components.
        
        Args:
            cls: The workflow class
            cls_instance: Instance of the workflow class
            ai_agent: AI agent instance
            entity_service: Service for entity operations
            cyoda_auth_service: Authentication service
            user_service: User service
            mock: Whether to run in mock mode
        """
        self.cls = cls
        self.cls_instance = cls_instance
        self.mock = mock
        
        # Initialize core components
        self.method_registry = MethodRegistry(cls, cls_instance)
        self.memory_manager = MemoryManager(entity_service, cyoda_auth_service)
        self.file_handler = FileHandler(entity_service, cyoda_auth_service)
        self.message_processor = MessageProcessor(self.memory_manager)
        
        # Initialize AI agent handler with dependencies
        self.ai_agent_handler = AIAgentHandler(
            ai_agent, self.method_registry, self.memory_manager, cls_instance, entity_service, cyoda_auth_service
        )
        
        # Initialize event processor with all dependencies
        self.event_processor = EventProcessor(
            self.method_registry,
            self.ai_agent_handler,
            self.memory_manager,
            self.file_handler,
            self.message_processor,
            user_service,
            entity_service,
            cyoda_auth_service,
            config_builder=ConfigBuilder()
        )
        
        # Store services for backward compatibility
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
        self.user_service = user_service
        
        # Expose methods_dict for backward compatibility
        self.methods_dict = self.method_registry.methods_dict
        
        logger.info(f"WorkflowDispatcher initialized with {len(self.methods_dict)} methods")
    
    async def process_event(self, entity: WorkflowEntity, processor_name: str,
                           technical_id: str) -> Tuple[WorkflowEntity, str]:
        """
        Process a workflow event.
        
        This is the main entry point for event processing. It delegates to the
        EventProcessor which coordinates all the specialized components.
        
        Args:
            entity: Workflow entity
            action: Action configuration
            technical_id: Technical identifier
            
        Returns:
            Tuple of (updated_entity, response)
        """
        try:
            return await self.event_processor.process_event(entity=entity, processor_name=processor_name, technical_id=technical_id)
        except Exception as e:
            logger.exception(f"Error in WorkflowDispatcher.process_event: {e}")
            entity.failed = True
            entity.error = f"Dispatcher error: {e}"
            return entity, f"Error: {e}"
    
    async def dispatch_function(self, function_name: str, **params) -> Any:
        """
        Dispatch a function call directly.
        
        This method provides backward compatibility with the original interface.
        
        Args:
            function_name: Name of the function to call
            **params: Parameters to pass to the function
            
        Returns:
            Function call result
        """
        try:
            return await self.method_registry.dispatch_method(method_name=function_name, **params)
        except Exception as e:
            logger.exception(f"Error dispatching function '{function_name}': {e}")
            return None
    
    def get_available_methods(self) -> list:
        """
        Get list of all available methods.
        
        Returns:
            List of method names
        """
        return self.method_registry.list_methods()
    
    def has_method(self, method_name: str) -> bool:
        """
        Check if a method is available.
        
        Args:
            method_name: Name of the method to check
            
        Returns:
            True if method exists, False otherwise
        """
        return self.method_registry.has_method(method_name)
    
    async def validate_configuration(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a workflow configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Validate AI agent config if present
            if config.get("type") in ("prompt", "agent", "batch"):
                return self.ai_agent_handler.validate_config(config)
            
            # Validate function config
            if config.get("type") == "function":
                function_config = config.get("function", {})
                function_name = function_config.get("name")
                
                if not function_name:
                    return False, "Function name is required"
                
                if not self.method_registry.has_method(function_name):
                    available = self.method_registry.list_methods()
                    return False, f"Function '{function_name}' not found. Available: {available}"
            
            return True, ""
            
        except Exception as e:
            logger.exception(f"Error validating configuration: {e}")
            return False, f"Validation error: {e}"
    
    def get_component_status(self) -> Dict[str, Any]:
        """
        Get status information about all components.
        
        Returns:
            Dictionary with component status information
        """
        return {
            "method_registry": {
                "methods_count": len(self.method_registry.methods_dict),
                "has_function_registry": hasattr(self.cls_instance, '_function_registry')
            },
            "memory_manager": {
                "initialized": self.memory_manager is not None
            },
            "ai_agent_handler": {
                "initialized": self.ai_agent_handler is not None
            },
            "file_handler": {
                "initialized": self.file_handler is not None
            },
            "message_processor": {
                "initialized": self.message_processor is not None
            },
            "event_processor": {
                "initialized": self.event_processor is not None
            }
        }
    
    # Backward compatibility methods
    async def _collect_subclass_methods(self):
        """Backward compatibility method."""
        return self.method_registry._collect_methods()
    
    async def _execute_method(self, method_name: str, technical_id: str, entity: WorkflowEntity):
        """Backward compatibility method."""
        return await self.method_registry.dispatch_method(
            method_name, technical_id=technical_id, entity=entity
        )
