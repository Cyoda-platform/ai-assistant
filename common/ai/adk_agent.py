"""
Google ADK Agent - Legacy compatibility wrapper.

This file provides backward compatibility for existing code while
redirecting to the new modular implementation in common/ai/adk/.

The new modular structure provides better separation of concerns,
improved testability, and cleaner architecture.

For new code, use: from common.ai.adk import AdkAgent
"""

import logging
from typing import Dict, Any, List, Optional

from common.ai.adk import AdkAgent as ModularAdkAgent
from common.ai.adk import AdkAgentContext as ModularAdkAgentContext
from entity.model import AIMessage

logger = logging.getLogger(__name__)


# Legacy compatibility aliases
AdkAgentContext = ModularAdkAgentContext


class AdkAgent:
    """
    Legacy compatibility wrapper for Google ADK Agent.
    
    This class provides backward compatibility for existing code while
    delegating all functionality to the new modular implementation.
    
    For new code, use: from common.ai.adk import AdkAgent
    """

    def __init__(self, max_calls: Optional[int] = None, mcp_servers: Optional[List[str]] = None):
        """
        Initialize the Google ADK Agent.

        Args:
            max_calls: Maximum number of agent iterations
            mcp_servers: List of MCP server names (legacy parameter, ignored)
        """
        # Import here to avoid circular imports
        from common.config.config import config
        
        if max_calls is None:
            max_calls = config.MAX_AI_AGENT_ITERATIONS
            
        self._modular_agent = ModularAdkAgent(max_calls=max_calls)
        
        if mcp_servers:
            logger.warning(f"MCP servers parameter ignored in modular implementation: {mcp_servers}")
            
        logger.warning(
            "Using legacy Google ADK Agent wrapper. "
            "Consider migrating to: from common.ai.adk import AdkAgent"
        )

    async def run_agent(self, methods_dict: Dict[str, Any], technical_id: str,
                       cls_instance: Any, entity: Any, tools: List[Dict[str, Any]],
                       model: Any, messages: List[AIMessage], tool_choice: str = "auto",
                       response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Legacy wrapper for run_agent method.
        
        Delegates to the modular implementation for actual functionality.
        """
        return await self._modular_agent.run_agent(
            methods_dict=methods_dict,
            technical_id=technical_id,
            cls_instance=cls_instance,
            entity=entity,
            tools=tools,
            model=model,
            messages=messages,
            tool_choice=tool_choice,
            response_format=response_format
        )

    @property
    def max_calls(self) -> int:
        """Get max_calls from the modular agent."""
        return self._modular_agent.max_calls

    def adapt_messages(self, messages: List[AIMessage]) -> List[Dict[str, str]]:
        """
        Legacy wrapper for message adaptation.
        
        Delegates to the modular implementation.
        """
        return self._modular_agent.message_adapter.adapt_messages(messages)

    async def cleanup(self):
        """
        Legacy cleanup method.
        
        The modular implementation handles cleanup automatically.
        """
        logger.debug("Legacy ADK cleanup called - no action needed with modular implementation")
