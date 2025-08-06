"""
ListDirectoryFiles1161ToolConfig Tool

Generated from config: workflow_configs/tools/list_directory_files_1161/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ListDirectoryFiles1161ToolConfig(FunctionProcessor):
    """Tool configuration for list_directory_files_1161"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ListDirectoryFiles1161ToolConfig.get_type()}.list_directory_files_1161"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "list_directory_files_1161"


# Create singleton instance
list_directory_files_1161_tool = ListDirectoryFiles1161ToolConfig()
