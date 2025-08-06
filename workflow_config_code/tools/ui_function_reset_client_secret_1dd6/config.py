"""
UiFunctionResetClientSecret1dd6ToolConfig Configuration

Generated from config: workflow_configs/tools/ui_function_reset_client_secret_1dd6/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "ui_function_reset_client_secret",
                "description": "Please use ui_function_reset_client_secret for requests like please reset the client secret for my technical user. Please use clientId from the user input. The user needs to explicitly give you clientId.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "method": {
                                        "type": "string",
                                        "enum": [
                                                "PUT"
                                        ]
                                },
                                "path": {
                                        "type": "string",
                                        "enum": [
                                                "/api/clients/{clientId}/secret"
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
