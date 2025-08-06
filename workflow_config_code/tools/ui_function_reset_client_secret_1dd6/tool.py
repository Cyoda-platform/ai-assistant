"""
UiFunctionResetClientSecret1dd6ToolConfig Tool

Generated from config: workflow_configs/tools/ui_function_reset_client_secret_1dd6/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class UiFunctionResetClientSecret1dd6ToolConfig(FunctionProcessor):
    """Tool configuration for ui_function_reset_client_secret_1dd6"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{UiFunctionResetClientSecret1dd6ToolConfig.get_type()}.ui_function_reset_client_secret_1dd6"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "ui_function_reset_client_secret_1dd6"


# Create singleton instance
ui_function_reset_client_secret_1dd6_tool = UiFunctionResetClientSecret1dd6ToolConfig()
