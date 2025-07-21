import inspect
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class MethodRegistry:
    """
    Handles method collection and registry management for workflow dispatching.
    Supports both traditional class methods and function registry patterns.
    """
    
    def __init__(self, cls, cls_instance):
        """
        Initialize the method registry.
        
        Args:
            cls: The class to collect methods from
            cls_instance: Instance of the class
        """
        self.cls = cls
        self.cls_instance = cls_instance
        self.methods_dict = self._collect_methods()
    
    def _collect_methods(self) -> Dict[str, Callable]:
        """
        Collect methods from the class, supporting both traditional class methods
        and the new function registry pattern used in refactored ChatWorkflow.
        
        Returns:
            Dictionary mapping method names to their implementations
        """
        methods = {}
        
        # First, collect traditional class methods using inspect
        for name, func in inspect.getmembers(self.cls, predicate=inspect.isfunction):
            key = f"{name}"
            methods[key] = func
        
        # Check if the class instance has a function registry (for refactored ChatWorkflow)
        if hasattr(self.cls_instance, '_function_registry'):
            logger.info("Found function registry in class instance, using registry methods")
            registry = self.cls_instance._function_registry
            for name, func in registry.items():
                # Create wrapper functions that match the expected signature
                # The registry functions are already bound to their service instances
                def create_wrapper(registry_func):
                    async def wrapper(cls_instance, technical_id, entity, **params):
                        # Call the registry function directly since it's already bound
                        return await registry_func(technical_id, entity, **params)
                    return wrapper
                
                # Store the wrapper in methods dict
                methods[name] = create_wrapper(func)
        
        logger.info(f"Collected {len(methods)} methods: {list(methods.keys())}")
        return methods
    
    def get_method(self, method_name: str) -> Callable:
        """
        Get a method by name.
        
        Args:
            method_name: Name of the method to retrieve
            
        Returns:
            The method implementation
            
        Raises:
            ValueError: If method not found
        """
        if method_name not in self.methods_dict:
            available_methods = list(self.methods_dict.keys())
            raise ValueError(f"Unknown method: {method_name}. Available methods: {available_methods}")
        
        return self.methods_dict[method_name]
    
    def has_method(self, method_name: str) -> bool:
        """
        Check if a method exists in the registry.
        
        Args:
            method_name: Name of the method to check
            
        Returns:
            True if method exists, False otherwise
        """
        return method_name in self.methods_dict
    
    def list_methods(self) -> list:
        """
        Get list of all available method names.
        
        Returns:
            List of method names
        """
        return list(self.methods_dict.keys())
    
    async def dispatch_method(self, method_name: str, **params) -> Any:
        """
        Dispatch a method call.

        Args:
            method_name: Name of the method to call
            **params: Parameters to pass to the method

        Returns:
            Result of the method call

        Raises:
            ValueError: If method not found
        """
        try:
            method = self.get_method(method_name=method_name)
            logger.debug(f"Dispatching method: {method_name}")

            # Check if this is a registry method (wrapped) or traditional method
            if hasattr(self.cls_instance, '_function_registry') and method_name in self.cls_instance._function_registry:
                # This is a registry method, call the wrapper
                return await method(cls_instance=self.cls_instance, **params)
            else:
                # This is a traditional method, call it on the instance
                bound_method = getattr(self.cls_instance, method_name)
                if inspect.iscoroutinefunction(bound_method):
                    return await bound_method(**params)
                else:
                    return bound_method(**params)
        except Exception as e:
            logger.exception(f"Error dispatching method '{method_name}': {e}")
            raise
