"""
InitChatsD512PyToolConfig Tool

Generated from config: workflow_configs/agents/tools/init_chats_d512_py/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class InitChatsD512PyToolConfig(FunctionProcessor):
    """Tool configuration for init_chats_d512_py"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{InitChatsD512PyToolConfig.get_type()}.init_chats_d512_py"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "init_chats_d512_py"


# Create singleton instance
init_chats_d512_py_tool = InitChatsD512PyToolConfig()
