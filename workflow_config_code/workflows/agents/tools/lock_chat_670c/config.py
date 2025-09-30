"""
LockChat670cToolConfig Configuration

Generated from config: workflow_configs/agents/tools/lock_chat_670c/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "lock_chat",
                "description": "Locks the chat to prevent user interaction during deployment",
                "strict": True
        }
}
