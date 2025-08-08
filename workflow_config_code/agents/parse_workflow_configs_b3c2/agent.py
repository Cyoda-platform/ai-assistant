"""
ParseWorkflowConfigsB3c2AgentConfig Agent

Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class ParseWorkflowConfigsB3c2AgentConfig(AgentProcessor):
    """Agent configuration for parse_workflow_configs_b3c2"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ParseWorkflowConfigsB3c2AgentConfig.get_type()}.parse_workflow_configs_b3c2"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
parse_workflow_configs_b3c2_agent = ParseWorkflowConfigsB3c2AgentConfig()
