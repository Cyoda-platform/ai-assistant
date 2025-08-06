"""
BuildGeneralApplicationF281ToolConfig Configuration

Generated from config: workflow_configs/tools/build_general_application_f281/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "build_general_application",
                "description": "Launches workflow that is necessary to build a new application. Do not use for editing existing applications. Do not ask user any additional information. Only Python with Cyoda framework are available.",
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
                                }
                        },
                        "required": [
                                "user_request",
                                "programming_language"
                        ],
                        "additionalProperties": False
                }
        }
}
