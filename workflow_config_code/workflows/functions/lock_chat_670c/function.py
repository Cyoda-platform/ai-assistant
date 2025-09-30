"""
LockChat670cFunctionConfig Function

Generated from config: workflow_configs/functions/lock_chat_670c/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class LockChat670cFunctionConfig(FunctionProcessor):
    """Function configuration for lock_chat_670c"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{LockChat670cFunctionConfig.get_type()}.lock_chat_670c"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "lock_chat_670c"


# Create singleton instance
lock_chat_670c_function = LockChat670cFunctionConfig()
