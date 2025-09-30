"""
IsChatLocked5b22FunctionConfig Function

Generated from config: workflow_configs/functions/is_chat_locked_5b22/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class IsChatLocked5b22FunctionConfig(FunctionProcessor):
    """Function configuration for is_chat_locked_5b22"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{IsChatLocked5b22FunctionConfig.get_type()}.is_chat_locked_5b22"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "is_chat_locked_5b22"


# Create singleton instance
is_chat_locked_5b22_function = IsChatLocked5b22FunctionConfig()
