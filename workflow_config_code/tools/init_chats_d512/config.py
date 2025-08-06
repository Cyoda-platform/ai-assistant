"""
InitChatsD512ToolConfig Configuration

Generated from config: workflow_configs/tools/init_chats_d512/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "init_chats",
                "description": "Initialises ai service"
        },
        "allow_anonymous_users": True
}
