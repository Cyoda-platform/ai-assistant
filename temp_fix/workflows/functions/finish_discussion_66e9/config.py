"""
FinishDiscussion66e9ToolConfig Configuration

Generated from config: workflow_configs/tools/finish_discussion_66e9/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "finish_discussion",
                "description": "Use if you have enough information or the user asks to proceed to the next question. Summarise the requirement in a couple of sentences and set to True if the user chooses your example answers or after 6 attempts! Do not hold the user too long.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "transition": {
                                        "type": "string",
                                        "enum": [
                                                "process_application_requirement"
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
