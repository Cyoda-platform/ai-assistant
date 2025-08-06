"""
IsChatLocked5b22ToolConfig Configuration

Generated from config: workflow_configs/tools/is_chat_locked_5b22/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "is_chat_locked",
                "description": "Verifies if the chat is locked"
        }
}
