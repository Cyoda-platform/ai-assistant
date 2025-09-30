"""
UiFunctionListAllTechnicalUsers7489ToolConfig Tool

Generated from config: workflow_configs/tools/ui_function_list_all_technical_users_7489/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class UiFunctionListAllTechnicalUsers7489ToolConfig(FunctionProcessor):
    """Tool configuration for ui_function_list_all_technical_users_7489"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{UiFunctionListAllTechnicalUsers7489ToolConfig.get_type()}.ui_function_list_all_technical_users_7489"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "ui_function_list_all_technical_users_7489"


# Create singleton instance
ui_function_list_all_technical_users_7489_tool = UiFunctionListAllTechnicalUsers7489ToolConfig()
