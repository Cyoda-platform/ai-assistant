"""
FinishConfigDiscussion0000ToolConfig Configuration

Generated from config: workflow_configs/tools/finish_prototype_discussion_0000/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
            "name": "finish_discussion",
            "description": "Finish the iteration if the user is happy with the result and has no more questions.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "transition": {
                        "type": "string",
                        "enum": [
                            "discuss_prototype"
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
