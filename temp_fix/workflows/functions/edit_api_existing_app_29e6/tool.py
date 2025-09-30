"""
EditApiExistingApp29e6ToolConfig Tool

Generated from config: workflow_configs/tools/edit_api_existing_app_29e6/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class EditApiExistingApp29e6ToolConfig(FunctionProcessor):
    """Tool configuration for edit_api_existing_app_29e6"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{EditApiExistingApp29e6ToolConfig.get_type()}.edit_api_existing_app_29e6"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "edit_api_existing_app_29e6"


# Create singleton instance
edit_api_existing_app_29e6_tool = EditApiExistingApp29e6ToolConfig()
