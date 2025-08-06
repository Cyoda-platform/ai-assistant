"""
ProcessUserInput9a8eAgentConfig Agent

Generated from config: workflow_configs/agents/process_user_input_9a8e/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class ProcessUserInput9a8eAgentConfig(AgentProcessor):
    """Agent configuration for process_user_input_9a8e"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ProcessUserInput9a8eAgentConfig.get_type()}.process_user_input_9a8e"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
process_user_input_9a8e_agent = ProcessUserInput9a8eAgentConfig()
