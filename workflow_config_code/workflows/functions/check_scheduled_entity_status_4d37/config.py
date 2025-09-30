"""
CheckScheduledEntityStatus4d37FunctionConfig Configuration

Generated from config: workflow_configs/functions/check_scheduled_entity_status_4d37/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "check_scheduled_entity_status",
                "description": "Checks the status of a scheduled entity",
                "strict": True
        }
}
