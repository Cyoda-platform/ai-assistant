"""
GetUserInfoD020ToolConfig Tool

Generated from config: workflow_configs/tools/get_user_info_d020/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class GetUserInfoD020ToolConfig(FunctionProcessor):
    """Tool configuration for get_user_info_d020"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{GetUserInfoD020ToolConfig.get_type()}.get_user_info_d020"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "get_user_info_d020"


# Create singleton instance
get_user_info_d020_tool = GetUserInfoD020ToolConfig()
