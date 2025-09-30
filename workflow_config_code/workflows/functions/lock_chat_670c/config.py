"""
LockChat670cFunctionConfig Configuration

Generated from config: workflow_configs/functions/lock_chat_670c/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "lock_chat",
                "description": "Locks the chat to prevent user interaction during deployment",
                "strict": True
        }
}
