"""
InitChatsForEditingE8f3FunctionConfig Function

Implements FunctionProcessor interface for editing workflow initialization.
Saves both original user request and current editing request.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class InitChatsForEditingE8f3FunctionConfig(FunctionProcessor):
    """Function configuration for init_chats_for_editing_e8f3"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{InitChatsForEditingE8f3FunctionConfig.get_type()}.init_chats_for_editing_e8f3"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "init_chats_for_editing_e8f3"


# Create singleton instance
init_chats_for_editing_e8f3_function = InitChatsForEditingE8f3FunctionConfig()
