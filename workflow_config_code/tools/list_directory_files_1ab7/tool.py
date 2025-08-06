"""
ListDirectoryFiles1ab7ToolConfig Tool

Generated from config: workflow_configs/tools/list_directory_files_1ab7/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ListDirectoryFiles1ab7ToolConfig(FunctionProcessor):
    """Tool configuration for list_directory_files_1ab7"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ListDirectoryFiles1ab7ToolConfig.get_type()}.list_directory_files_1ab7"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "list_directory_files_1ab7"


# Create singleton instance
list_directory_files_1ab7_tool = ListDirectoryFiles1ab7ToolConfig()
