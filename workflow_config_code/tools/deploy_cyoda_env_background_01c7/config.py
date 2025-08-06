"""
DeployCyodaEnvBackground01c7ToolConfig Configuration

Generated from config: workflow_configs/tools/deploy_cyoda_env_background_01c7/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "deploy_cyoda_env_background",
                "description": "Launches workflow that is necessary to deploy Cyoda environment for the user. User needs to explicitly ask for deployment of Cyoda environment.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "user_request": {
                                        "type": "string"
                                },
                                "transition": {
                                        "type": "string",
                                        "enum": [
                                                "process_app_setup_3"
                                        ]
                                }
                        },
                        "required": [
                                "user_request",
                                "transition"
                        ],
                        "additionalProperties": False
                }
        }
}
