"""
PromptSent956fAgentConfig Agent

Generated from config: workflow_configs/agents/prompt_sent_956f/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class PromptSent956fAgentConfig(AgentProcessor):
    """Agent configuration for prompt_sent_956f"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{PromptSent956fAgentConfig.get_type()}.prompt_sent_956f"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
prompt_sent_956f_agent = PromptSent956fAgentConfig()
