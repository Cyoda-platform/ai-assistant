"""
Context classes for Google ADK Agent.

Provides context objects for dependency injection and state management
throughout the agent execution lifecycle.
"""

from typing import Dict, Any


class AdkAgentContext:
    """
    Context object for dependency injection in Google ADK.
    
    Contains all the necessary context information for tool execution,
    including method registry, technical identifiers, and entity data.
    """

    def __init__(self, methods_dict: Dict[str, Any], technical_id: str,
                 cls_instance: Any, entity: Any):
        """
        Initialize the agent context.
        
        Args:
            methods_dict: Dictionary of available methods/tools
            technical_id: Technical identifier for the session
            cls_instance: Class instance for method calls
            entity: Entity object for context
        """
        self.methods_dict = methods_dict or {}
        self.technical_id = technical_id
        self.cls_instance = cls_instance
        self.entity = entity

    def has_method(self, method_name: str) -> bool:
        """
        Check if a method is available in the context.
        
        Args:
            method_name: Name of the method to check
            
        Returns:
            True if method is available, False otherwise
        """
        return method_name in self.methods_dict

    def get_method(self, method_name: str) -> Any:
        """
        Get a method from the context.
        
        Args:
            method_name: Name of the method to retrieve
            
        Returns:
            Method object
            
        Raises:
            KeyError: If method is not found
        """
        if not self.has_method(method_name):
            raise KeyError(f"Method '{method_name}' not found in context")
        return self.methods_dict[method_name]

    def get_context_params(self) -> Dict[str, Any]:
        """
        Get standard context parameters for method injection.
        
        Returns:
            Dictionary with technical_id and entity
        """
        return {
            'technical_id': self.technical_id,
            'entity': self.entity
        }

    def __repr__(self) -> str:
        """String representation of the context."""
        return (f"AdkAgentContext(technical_id='{self.technical_id}', "
                f"methods_count={len(self.methods_dict)}, "
                f"entity_type={type(self.entity).__name__})")
