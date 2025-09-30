"""
TriggerParentEntityB4c4FunctionConfig Configuration

Generated from config: workflow_configs/functions/trigger_parent_entity_b4c4/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "trigger_parent_entity",
                "description": "Triggers the parent entity after completion",
                "strict": True
        }
}
