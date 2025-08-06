"""
PromptSent59d6AgentConfig Agent

Generated from config: workflow_configs/agents/prompt_sent_59d6/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class PromptSent59d6AgentConfig(AgentProcessor):
    """Agent configuration for prompt_sent_59d6"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{PromptSent59d6AgentConfig.get_type()}.prompt_sent_59d6"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
prompt_sent_59d6_agent = PromptSent59d6AgentConfig()
