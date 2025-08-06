"""
UiFunctionIssueTechnicalUser808aToolConfig Configuration

Generated from config: workflow_configs/tools/ui_function_issue_technical_user_808a/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "ui_function_issue_technical_user",
                "description": "Please use ui_function_issue_technical_user for requests like give me a technical user or give me credentials (CYODA_CLIENT_ID and CYODA_CLIENT_SECRET). This will return CYODA_CLIENT_ID and CYODA_CLIENT_SECRET.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "method": {
                                        "type": "string",
                                        "enum": [
                                                "POST"
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
                                                "file"
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
