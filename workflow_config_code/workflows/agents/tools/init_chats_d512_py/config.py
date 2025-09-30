"""
InitChatsD512PyToolConfig Configuration

Generated from config: workflow_configs/agents/tools/init_chats_d512_py/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
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
        "allow_anonymous_users": True,
        "output": {
                "local_fs": [
                        "application/resources/functional_requirements/user_requirement.md"
                ]
        }
}
