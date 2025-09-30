"""
GetUserInfoD020ToolConfig Configuration

Generated from config: workflow_configs/tools/get_user_info_d020/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "get_user_info",
                "description": "Use this tool to get user information like user environment URL, user branch name etc",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "user_request": {
                                        "type": "string"
                                }
                        },
                        "required": [
                                "user_request"
                        ],
                        "additionalProperties": False
                }
        }
}
