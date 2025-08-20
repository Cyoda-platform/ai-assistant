"""Base Processor class for workflow processors."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from workflow.dispatcher.events.processing_context import ProcessingContext
from workflow.dispatcher.actions.action import Action
from workflow.dispatcher.interfaces.memory_manager import MemoryManager
from entity.chat.chat import AgenticFlowEntity
from entity.model import ChatMemory


class Processor(ABC):
    """Base class for all processors."""

    @abstractmethod
    async def execute(self, ctx: ProcessingContext, action: Action) -> str:
        """Execute the processor logic."""
        pass



