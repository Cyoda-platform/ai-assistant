"""
ReadLinkC472ToolConfig Tool

Generated from config: workflow_configs/tools/read_link_c472/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ReadLinkC472ToolConfig(FunctionProcessor):
    """Tool configuration for read_link_c472"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ReadLinkC472ToolConfig.get_type()}.read_link_c472"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "read_link_c472"


# Create singleton instance
read_link_c472_tool = ReadLinkC472ToolConfig()
