"""
DefineFunctionalRequirements8ee2AgentConfig Agent

Generated from config: workflow_configs/agents/define_functional_requirements_8ee2/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class DefineFunctionalRequirements8ee2AgentConfig(AgentProcessor):
    """Agent configuration for define_functional_requirements_8ee2"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{DefineFunctionalRequirements8ee2AgentConfig.get_type()}.define_functional_requirements_8ee2"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
define_functional_requirements_8ee2_agent = DefineFunctionalRequirements8ee2AgentConfig()
