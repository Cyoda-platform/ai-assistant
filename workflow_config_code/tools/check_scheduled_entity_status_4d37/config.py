"""
CheckScheduledEntityStatus4d37ToolConfig Configuration

Generated from config: workflow_configs/tools/check_scheduled_entity_status_4d37/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "check_scheduled_entity_status",
                "description": "Checks the status of a scheduled entity",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                }
        }
}
