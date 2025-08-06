"""
ReadLink16a6ToolConfig Tool

Generated from config: workflow_configs/tools/read_link_16a6/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ReadLink16a6ToolConfig(FunctionProcessor):
    """Tool configuration for read_link_16a6"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ReadLink16a6ToolConfig.get_type()}.read_link_16a6"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "read_link_16a6"


# Create singleton instance
read_link_16a6_tool = ReadLink16a6ToolConfig()
