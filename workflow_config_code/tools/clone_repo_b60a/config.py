"""
CloneRepoB60aToolConfig Configuration

Generated from config: workflow_configs/tools/clone_repo_b60a/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "clone_repo",
                "description": "Clones template repository"
        },
        "publish": True,
        "allow_anonymous_users": True
}
