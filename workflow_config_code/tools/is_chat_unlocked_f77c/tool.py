"""
IsChatUnlockedF77cToolConfig Tool

Generated from config: workflow_configs/tools/is_chat_unlocked_f77c/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class IsChatUnlockedF77cToolConfig(FunctionProcessor):
    """Tool configuration for is_chat_unlocked_f77c"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{IsChatUnlockedF77cToolConfig.get_type()}.is_chat_unlocked_f77c"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "is_chat_unlocked_f77c"


# Create singleton instance
is_chat_unlocked_f77c_tool = IsChatUnlockedF77cToolConfig()
