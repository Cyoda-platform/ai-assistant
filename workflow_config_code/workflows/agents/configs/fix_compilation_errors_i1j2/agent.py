"""
FixCompilationErrorsI1j2AgentConfig Agent

Generated from config: workflow_configs/agents/configs/fix_compilation_errors_i1j2/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class FixCompilationErrorsI1j2AgentConfig(AgentProcessor):
    """Agent configuration for fix_compilation_errors_i1j2"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{FixCompilationErrorsI1j2AgentConfig.get_type()}.fix_compilation_errors_i1j2"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
fix_compilation_errors_i1j2_agent = FixCompilationErrorsI1j2AgentConfig()
