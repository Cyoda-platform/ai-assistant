"""
InitChatsForEditingE8f3FunctionConfig Configuration

Configuration for initializing chats in the editing workflow.
Saves both original user request and current editing request.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "init_chats_for_editing",
                "description": "Initialises ai service for editing workflow with original and editing requirements",
                "parameters": {
                        "JAVA": "src/main/resources/functional_requirements",
                        "PYTHON": "application/resources/functional_requirements"
                }
        },
        "allow_anonymous_users": True
}
