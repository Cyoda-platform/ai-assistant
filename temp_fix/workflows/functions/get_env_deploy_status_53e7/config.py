"""
GetEnvDeployStatus53e7ToolConfig Configuration

Generated from config: workflow_configs/tools/get_env_deploy_status_53e7/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "get_env_deploy_status",
                "description": "Use if the user wants to know the status of their environment build/deploy.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "build_id": {
                                        "type": "string"
                                }
                        },
                        "required": [
                                "build_id"
                        ],
                        "additionalProperties": False
                }
        }
}
