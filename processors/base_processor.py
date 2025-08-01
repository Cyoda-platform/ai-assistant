"""
Base processor interface for the Cyoda AI Workflow Framework.

This module defines the abstract base class that all processors must implement.
Processors are responsible for executing specific types of actions within workflows.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ProcessorContext:
    """Context information passed to processors during execution."""
    
    workflow_name: str
    state_name: str
    transition_name: str
    entity_id: Optional[str] = None
    entity_data: Optional[Any] = None  # Can be entity object or dict for backward compatibility
    memory_tags: Optional[list] = None
    execution_mode: str = "SYNC"
    config: Optional[Dict[str, Any]] = None


@dataclass
class ProcessorResult:
    """Result returned by processor execution."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    memory_updates: Optional[Dict[str, Any]] = None
    next_state: Optional[str] = None


class BaseProcessor(ABC):
    """
    Abstract base class for all workflow processors.
    
    Processors handle the execution of specific actions within workflows,
    separating orchestration logic from execution logic.
    """
    
    def __init__(self, processor_name: str):
        """
        Initialize the processor.
        
        Args:
            processor_name: Unique name identifying this processor
        """
        self.processor_name = processor_name
    
    @abstractmethod
    def supports(self, processor_name: str) -> bool:
        """
        Check if this processor supports the given processor name.
        
        Args:
            processor_name: Name of the processor to check
            
        Returns:
            True if this processor can handle the given name
        """
        pass
    
    @abstractmethod
    async def execute(self, context: ProcessorContext) -> ProcessorResult:
        """
        Execute the processor with the given context.

        Args:
            context: Execution context containing workflow and entity information

        Returns:
            ProcessorResult containing execution outcome and any updates
        """
        pass
    
    def validate_context(self, context: ProcessorContext) -> bool:
        """
        Validate that the context contains required information.
        
        Args:
            context: Execution context to validate
            
        Returns:
            True if context is valid for this processor
        """
        return context.workflow_name is not None and context.state_name is not None
    
    def create_success_result(
        self, 
        data: Optional[Dict[str, Any]] = None,
        memory_updates: Optional[Dict[str, Any]] = None,
        next_state: Optional[str] = None
    ) -> ProcessorResult:
        """
        Create a successful processor result.
        
        Args:
            data: Optional result data
            memory_updates: Optional memory updates to apply
            next_state: Optional next state to transition to
            
        Returns:
            ProcessorResult indicating success
        """
        return ProcessorResult(
            success=True,
            data=data,
            memory_updates=memory_updates,
            next_state=next_state
        )
    
    def create_error_result(self, error_message: str) -> ProcessorResult:
        """
        Create an error processor result.
        
        Args:
            error_message: Description of the error
            
        Returns:
            ProcessorResult indicating failure
        """
        return ProcessorResult(
            success=False,
            error_message=error_message
        )


class ProcessorRegistry:
    """Registry for managing processor instances."""
    
    def __init__(self):
        self._processors: Dict[str, BaseProcessor] = {}
    
    def register(self, processor: BaseProcessor) -> None:
        """
        Register a processor instance.
        
        Args:
            processor: Processor instance to register
        """
        self._processors[processor.processor_name] = processor
    
    def get_processor(self, processor_name: str) -> Optional[BaseProcessor]:
        """
        Get a processor by name.

        Args:
            processor_name: Name of the processor to retrieve (e.g., "AgentProcessor.chat_entity_submitted_workflow_question_submit_answer")

        Returns:
            Processor instance if found, None otherwise
        """
        # Direct lookup first
        if processor_name in self._processors:
            return self._processors[processor_name]

        # Check if any processor supports this name (handles underscore naming convention)
        for processor in self._processors.values():
            if processor.supports(processor_name):
                return processor

        return None
    
    def list_processors(self) -> list:
        """
        List all registered processor names.
        
        Returns:
            List of processor names
        """
        return list(self._processors.keys())


# Global processor registry instance
processor_registry = ProcessorRegistry()
