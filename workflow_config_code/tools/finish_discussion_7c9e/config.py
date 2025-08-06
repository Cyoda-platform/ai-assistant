"""
FinishDiscussion7c9eToolConfig Configuration

Generated from config: workflow_configs/tools/finish_discussion_7c9e/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "finish_discussion",
                "description": "Use if the user asks to proceed or if the user is satisfied with the current result (e.g. says it is correct, valid, works for them). If set to False notify the user you're going to proceed with prototype generation.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "transition": {
                                        "type": "string",
                                        "enum": [
                                                "discuss_api"
                                        ]
                                }
                        },
                        "required": [
                                "transition"
                        ],
                        "additionalProperties": False
                }
        }
}
