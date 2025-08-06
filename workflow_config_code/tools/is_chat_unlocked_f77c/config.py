"""
IsChatUnlockedF77cToolConfig Configuration

Generated from config: workflow_configs/tools/is_chat_unlocked_f77c/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "is_chat_unlocked",
                "description": "Verifies if the chat is unlocked"
        }
}
