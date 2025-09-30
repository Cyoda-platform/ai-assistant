"""
UiFunctionListAllTechnicalUsers7489ToolConfig Configuration

Generated from config: workflow_configs/tools/ui_function_list_all_technical_users_7489/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "ui_function_list_all_technical_users",
                "description": "Please use ui_function_list_all_technical_users for requests like give me all technical/m2m users. This will return the list of M2M clients.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "method": {
                                        "type": "string",
                                        "enum": [
                                                "GET"
                                        ]
                                },
                                "path": {
                                        "type": "string",
                                        "enum": [
                                                "/api/clients"
                                        ]
                                },
                                "response_format": {
                                        "type": "string",
                                        "enum": [
                                                "text"
                                        ]
                                }
                        },
                        "required": [
                                "method",
                                "path",
                                "response_format"
                        ],
                        "additionalProperties": False
                }
        }
}
