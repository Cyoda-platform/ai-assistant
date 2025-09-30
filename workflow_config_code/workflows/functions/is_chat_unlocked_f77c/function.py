"""
IsChatUnlockedF77cFunctionConfig Function

Generated from config: workflow_configs/functions/is_chat_unlocked_f77c/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class IsChatUnlockedF77cFunctionConfig(FunctionProcessor):
    """Function configuration for is_chat_unlocked_f77c"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{IsChatUnlockedF77cFunctionConfig.get_type()}.is_chat_unlocked_f77c"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "is_chat_unlocked_f77c"


# Create singleton instance
is_chat_unlocked_f77c_function = IsChatUnlockedF77cFunctionConfig()
