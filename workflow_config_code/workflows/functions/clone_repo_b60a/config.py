"""
CloneRepoB60aFunctionConfig Configuration

Generated from config: workflow_configs/functions/clone_repo_b60a/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "clone_repo",
                "description": "Clones template repository"
        },
        "publish": True,
        "allow_anonymous_users": True
}
