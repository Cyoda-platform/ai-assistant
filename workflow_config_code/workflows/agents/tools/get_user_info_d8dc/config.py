"""
GetUserInfoD8dcToolConfig Configuration

Generated from config: workflow_configs/agents/tools/get_user_info_d8dc/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "get_user_info",
                "description": "Use this tool to get comprehensive user and workflow information including: user authentication status, Cyoda environment URL and deployment status, repository details (git branch, repository name, URL, installation ID), programming language, workflow state and name, build/deployment status, user requests, file attachments, and any other workflow cache data. This provides the complete context needed to understand the user's current application development state.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "user_request": {
                                        "type": "string",
                                        "description": "The user's request or query for context"
                                }
                        },
                        "required": [
                                "user_request"
                        ],
                        "additionalProperties": False
                }
        }
}
