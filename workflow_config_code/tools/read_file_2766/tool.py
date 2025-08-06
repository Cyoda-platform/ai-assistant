"""
ReadFile2766ToolConfig Tool

Generated from config: workflow_configs/tools/read_file_2766/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ReadFile2766ToolConfig(FunctionProcessor):
    """Tool configuration for read_file_2766"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ReadFile2766ToolConfig.get_type()}.read_file_2766"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "read_file_2766"


# Create singleton instance
read_file_2766_tool = ReadFile2766ToolConfig()
