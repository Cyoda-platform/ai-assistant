"""ConfigBasedAgentProcessor for agent processors with AI agent handler injection."""

from typing import Dict, Any
from entity.chat.chat import AgenticFlowEntity
from entity.model import ChatMemory
from workflow.dispatcher.interfaces.memory_manager import MemoryManager
from .agent_processor import AgentProcessor


class ConfigBasedAgentProcessor(AgentProcessor):
    """Agent processor that uses ai_agent_handler with injection support"""

    def __init__(self, ai_agent_handler=None, memory_manager: MemoryManager = None):
        super().__init__(memory_manager)
        self.ai_agent_handler = ai_agent_handler
        self._services = None

    async def execute(self, ctx, action) -> str:
        """Override execute to store services context"""
        # Store services for ai_agent_handler access
        self._services = ctx.services

        # Call parent template method
        return await super().execute(ctx, action)

    async def execute_agent_logic(self, config: Dict[str, Any], entity: AgenticFlowEntity,
                                 memory: ChatMemory, technical_id: str) -> str:
        """Execute using ai_agent_handler (injectable)"""
        handler = self.get_ai_agent_handler()
        if not handler:
            return "Error: No AI agent handler available"

        return await handler.run_ai_agent(config, entity, memory, technical_id)

    def get_ai_agent_handler(self):
        """Get ai_agent_handler - uses injected one or falls back to services"""
        if self.ai_agent_handler:
            return self.ai_agent_handler

        # Get from services (set during execution)
        if self._services:
            return self._services.ai_agent_handler

        return None

    def set_ai_agent_handler(self, handler) -> None:
        """Injection point for custom AI agent handlers"""
        self.ai_agent_handler = handler

    def get_name(self) -> str:
        """Get the processor name (from interfaces pattern) - to be overridden"""
        return f"{self.get_type()}.config_based_agent"

    def get_config(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get processor config (from interfaces pattern) - to be overridden"""
        return {}
