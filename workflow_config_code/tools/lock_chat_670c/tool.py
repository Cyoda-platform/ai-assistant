"""
LockChat670cToolConfig Tool

Generated from config: workflow_configs/tools/lock_chat_670c/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class LockChat670cToolConfig(FunctionProcessor):
    """Tool configuration for lock_chat_670c"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{LockChat670cToolConfig.get_type()}.lock_chat_670c"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "lock_chat_670c"


# Create singleton instance
lock_chat_670c_tool = LockChat670cToolConfig()
