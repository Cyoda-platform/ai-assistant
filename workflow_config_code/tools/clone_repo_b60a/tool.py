"""
CloneRepoB60aToolConfig Tool

Generated from config: workflow_configs/tools/clone_repo_b60a/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class CloneRepoB60aToolConfig(FunctionProcessor):
    """Tool configuration for clone_repo_b60a"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{CloneRepoB60aToolConfig.get_type()}.clone_repo_b60a"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "clone_repo_b60a"


# Create singleton instance
clone_repo_b60a_tool = CloneRepoB60aToolConfig()
