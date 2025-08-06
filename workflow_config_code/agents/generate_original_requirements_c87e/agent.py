"""
GenerateOriginalRequirementsC87eAgentConfig Agent

Generated from config: workflow_configs/agents/generate_original_requirements_c87e/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class GenerateOriginalRequirementsC87eAgentConfig(AgentProcessor):
    """Agent configuration for generate_original_requirements_c87e"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{GenerateOriginalRequirementsC87eAgentConfig.get_type()}.generate_original_requirements_c87e"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
generate_original_requirements_c87e_agent = GenerateOriginalRequirementsC87eAgentConfig()
