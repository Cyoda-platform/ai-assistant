"""
FinishDiscussion8f05ToolConfig Configuration

Generated from config: workflow_configs/tools/finish_discussion_8f05/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "finish_discussion",
                "description": "Use if the user is ready to proceed or asks to proceed to the next question. If the user wants to go to the next step - use immediately.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "transition": {
                                        "type": "string",
                                        "enum": [
                                                "process_app_setup_4"
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
