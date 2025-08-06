"""
IsChatLocked5b22ToolConfig Tool

Generated from config: workflow_configs/tools/is_chat_locked_5b22/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class IsChatLocked5b22ToolConfig(FunctionProcessor):
    """Tool configuration for is_chat_locked_5b22"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{IsChatLocked5b22ToolConfig.get_type()}.is_chat_locked_5b22"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "is_chat_locked_5b22"


# Create singleton instance
is_chat_locked_5b22_tool = IsChatLocked5b22ToolConfig()
