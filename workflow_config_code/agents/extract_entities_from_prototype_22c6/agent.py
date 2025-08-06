"""
ExtractEntitiesFromPrototype22c6AgentConfig Agent

Generated from config: workflow_configs/agents/extract_entities_from_prototype_22c6/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class ExtractEntitiesFromPrototype22c6AgentConfig(AgentProcessor):
    """Agent configuration for extract_entities_from_prototype_22c6"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ExtractEntitiesFromPrototype22c6AgentConfig.get_type()}.extract_entities_from_prototype_22c6"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
extract_entities_from_prototype_22c6_agent = ExtractEntitiesFromPrototype22c6AgentConfig()
