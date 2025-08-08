"""
SaveFunctionalRequirementsF2a1AgentConfig Agent

Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class SaveFunctionalRequirementsF2a1AgentConfig(AgentProcessor):
    """Agent configuration for save_functional_requirements_f2a1"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{SaveFunctionalRequirementsF2a1AgentConfig.get_type()}.save_functional_requirements_f2a1"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
save_functional_requirements_f2a1_agent = SaveFunctionalRequirementsF2a1AgentConfig()
