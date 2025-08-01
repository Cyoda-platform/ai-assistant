"""
Base Workflow Classes.

This module provides the base workflow classes that were previously in entity/workflow.py.
These are kept for backward compatibility with existing code.
"""

import logging
from abc import ABC

logger = logging.getLogger(__name__)

# Global process dispatch dictionary for backward compatibility
process_dispatch = {}


class Workflow(ABC):
    """
    Abstract base class for workflows.
    
    This class provides the basic interface that all workflows should implement.
    It's kept for backward compatibility with existing code.
    """
    pass


class BaseWorkflow(Workflow):
    """
    Base workflow implementation with common functionality.
    
    This class can be extended by specific workflow implementations
    that need common workflow functionality.
    """
    
    def __init__(self, workflow_name: str = None):
        """
        Initialize the base workflow.
        
        Args:
            workflow_name: Name of the workflow
        """
        self.workflow_name = workflow_name
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def get_workflow_name(self) -> str:
        """
        Get the workflow name.
        
        Returns:
            Workflow name
        """
        return self.workflow_name or self.__class__.__name__
    
    def log_info(self, message: str) -> None:
        """
        Log an info message.
        
        Args:
            message: Message to log
        """
        self.logger.info(f"[{self.get_workflow_name()}] {message}")
    
    def log_error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: Message to log
        """
        self.logger.error(f"[{self.get_workflow_name()}] {message}")
    
    def log_debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: Message to log
        """
        self.logger.debug(f"[{self.get_workflow_name()}] {message}")


# Backward compatibility exports
__all__ = ['Workflow', 'BaseWorkflow', 'process_dispatch']
