"""
GenerateFunctionalRequirementsAcccAgentConfig Agent

Generated from config: workflow_configs/agents/generate_functional_requirements_accc/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class GenerateFunctionalRequirementsAcccAgentConfig(AgentProcessor):
    """Agent configuration for generate_functional_requirements_accc"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{GenerateFunctionalRequirementsAcccAgentConfig.get_type()}.generate_functional_requirements_accc"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
generate_functional_requirements_accc_agent = GenerateFunctionalRequirementsAcccAgentConfig()
