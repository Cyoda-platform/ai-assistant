"""
BuildGeneralApplicationF281ToolConfig Configuration

Generated from config: workflow_configs/agents/tools/build_general_application_f281/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "build_general_application",
                "description": "Launches workflow to build a new application. Supports both public repositories (default Cyoda templates) and private repositories (user's own codebase). For private repositories, requires installation_id and repository_url. Do not use for editing existing applications. Only Java and Python with Cyoda framework are available. Pass full user request as is.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "user_request": {
                                        "type": "string"
                                },
                                "programming_language": {
                                        "type": "string",
                                        "enum": [
                                                "JAVA",
                                                "PYTHON"
                                        ]
                                },
                                "mode": {
                                        "type": "string",
                                        "enum": [
                                                #"regular",
                                                "optimized"
                                        ]
                                },
                                "installation_id": {
                                    "type": "string"
                                },
                                "repository_url": {
                                    "type": "string",
                                }
                        },
                        "required": [
                                "user_request",
                                "programming_language",
                                "mode",
                                "installation_id",
                                "repository_url"
                        ],
                        "additionalProperties": False
                }
        }
}
