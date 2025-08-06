"""
EnrichWorkflowF2c6AgentConfig Agent

Generated from config: workflow_configs/agents/enrich_workflow_f2c6/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class EnrichWorkflowF2c6AgentConfig(AgentProcessor):
    """Agent configuration for enrich_workflow_f2c6"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{EnrichWorkflowF2c6AgentConfig.get_type()}.enrich_workflow_f2c6"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
enrich_workflow_f2c6_agent = EnrichWorkflowF2c6AgentConfig()
