"""
InitChatsD512FunctionConfig Configuration

Generated from config: workflow_configs/functions/init_chats_d512/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "init_chats",
                "description": "Initialises ai service",
                "parameters": {
                        "JAVA": "src/main/resources/functional_requirements",
                        "PYTHON": "application/resources/functional_requirements"
                }
        },
        "allow_anonymous_users": True
}
