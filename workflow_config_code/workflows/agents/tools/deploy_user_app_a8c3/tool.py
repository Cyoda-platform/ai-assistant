"""
DeployUserAppA8c3ToolConfig Tool

Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class DeployUserAppA8c3ToolConfig(FunctionProcessor):
    """Tool configuration for deploy_user_app_a8c3"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{DeployUserAppA8c3ToolConfig.get_type()}.deploy_user_app_a8c3"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "deploy_user_app_a8c3"


# Create singleton instance
deploy_user_app_a8c3_tool = DeployUserAppA8c3ToolConfig()

