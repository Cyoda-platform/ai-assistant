"""
EditAppJavaAgentConfig Agent

Agent for editing existing Java applications.
Uses editing-specific prompt that scans functional_requirements for editing requirements.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class EditAppJavaAgentConfig(AgentProcessor):
    """Agent configuration for edit_app_java"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{EditAppJavaAgentConfig.get_type()}.edit_app_java"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
edit_app_java_agent = EditAppJavaAgentConfig()
