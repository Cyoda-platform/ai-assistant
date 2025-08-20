"""AgentProcessor template for AI agent actions."""

from abc import abstractmethod
from typing import Dict, Any
from entity.chat.chat import AgenticFlowEntity
from entity.model import ChatMemory
from workflow.dispatcher.events.processing_context import ProcessingContext
from workflow.dispatcher.actions.action import Action
from workflow.dispatcher.interfaces.memory_manager import MemoryManager
from .processor import Processor


class AgentProcessor(Processor):
    """Template AgentProcessor that handles common workflow and delegates to subclasses"""

    def __init__(self, memory_manager: MemoryManager = None):
        self.memory_manager = memory_manager

    async def execute(self, ctx: ProcessingContext, action: Action) -> str:
        """Template method implementing the common agent workflow"""

        # Step 1: Validate entity type
        if not self.validate_entity(ctx.event.entity):
            return "Error: AgentProcessor requires AgenticFlowEntity"

        # Step 2: Get memory manager (injectable)
        memory_manager = self.get_memory_manager(ctx)

        # Step 3: Get chat memory
        chat_memory = await memory_manager.get_chat_memory(
            memory_id=ctx.event.entity.memory_id
        )

        # Step 4: Execute agent logic (delegated to child)
        response = await self.execute_agent_logic(
            config=action.config,
            entity=ctx.event.entity,
            memory=chat_memory,
            technical_id=ctx.event.technical_id
        )

        # Step 5: Update chat memory
        await memory_manager.update_chat_memory(
            memory_id=ctx.event.entity.memory_id,
            chat_memory=chat_memory
        )

        # Step 6: Post-process response
        return self.post_process_response(response)

    def validate_entity(self, entity) -> bool:
        """Validate entity type - can be overridden"""
        return isinstance(entity, AgenticFlowEntity)

    def get_memory_manager(self, ctx) -> MemoryManager:
        """Get memory manager - injectable"""
        return self.memory_manager or ctx.services.get_memory_manager()

    @abstractmethod
    async def execute_agent_logic(self, config: Dict[str, Any], entity: AgenticFlowEntity,
                                 memory: ChatMemory, technical_id: str) -> str:
        """Abstract method for child classes to implement agent logic"""
        pass

    def post_process_response(self, response: str) -> str:
        """Hook for post-processing response - can be overridden"""
        return response

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return "AgentProcessor"

    def get_name(self) -> str:
        """Get the processor name - to be overridden by subclasses"""
        return f"{self.get_type()}.agent_processor"

    def get_config(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get processor config - to be overridden by subclasses"""
        return {}
