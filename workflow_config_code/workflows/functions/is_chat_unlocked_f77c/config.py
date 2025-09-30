"""
IsChatUnlockedF77cFunctionConfig Configuration

Generated from config: workflow_configs/functions/is_chat_unlocked_f77c/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "is_chat_unlocked",
                "description": "Verifies if the chat is unlocked"
        }
}
