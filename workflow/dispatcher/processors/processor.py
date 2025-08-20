"""Base Processor class for workflow processors."""

from abc import ABC, abstractmethod
from workflow.dispatcher.events.processing_context import ProcessingContext
from workflow.dispatcher.actions.action import Action


class Processor(ABC):
    """Base class for all processors."""
    
    @abstractmethod
    async def execute(self, ctx: ProcessingContext, action: Action) -> str:
        """Execute the processor logic."""
        pass
