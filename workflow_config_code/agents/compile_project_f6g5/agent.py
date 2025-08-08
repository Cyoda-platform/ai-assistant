"""
CompileProjectF6g5AgentConfig Agent

Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class CompileProjectF6g5AgentConfig(AgentProcessor):
    """Agent configuration for compile_project_f6g5"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{CompileProjectF6g5AgentConfig.get_type()}.compile_project_f6g5"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
compile_project_f6g5_agent = CompileProjectF6g5AgentConfig()
