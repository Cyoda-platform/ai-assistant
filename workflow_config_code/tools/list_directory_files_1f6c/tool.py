"""
ListDirectoryFiles1f6cToolConfig Tool

Generated from config: workflow_configs/tools/list_directory_files_1f6c/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ListDirectoryFiles1f6cToolConfig(FunctionProcessor):
    """Tool configuration for list_directory_files_1f6c"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ListDirectoryFiles1f6cToolConfig.get_type()}.list_directory_files_1f6c"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "list_directory_files_1f6c"


# Create singleton instance
list_directory_files_1f6c_tool = ListDirectoryFiles1f6cToolConfig()
