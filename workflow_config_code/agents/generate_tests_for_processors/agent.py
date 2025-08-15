"""
GenerateTestsForProcessorsAgentConfig Configuration

Agent configuration for reviewing and enhancing processors to ensure they satisfy functional requirements.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class GenerateTestsForProcessorsAgentConfig(AgentProcessor):
    """Configuration for the enhance processors agent"""

    @staticmethod
    def get_type() -> str:
        """Get the agent type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{GenerateTestsForProcessorsAgentConfig.get_type()}.generate_tests_for_processors"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
generate_tests_for_processors_agent = GenerateTestsForProcessorsAgentConfig()
