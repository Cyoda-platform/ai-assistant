"""
PromptSentA239PyAgentConfig Agent

Generated from config: workflow_configs/agents/prompt_sent_a239_py/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class PromptSentA239PyAgentConfig(AgentProcessor):
    """Agent configuration for prompt_sent_a239_py"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{PromptSentA239PyAgentConfig.get_type()}.prompt_sent_a239_py"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
prompt_sent_a239_py_agent = PromptSentA239PyAgentConfig()
