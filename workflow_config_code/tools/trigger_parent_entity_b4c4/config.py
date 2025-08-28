"""
TriggerParentEntityB4c4ToolConfig Configuration

Generated from config: workflow_configs/tools/trigger_parent_entity_b4c4/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "trigger_parent_entity",
                "description": "Triggers the parent entity after completion",
                "strict": True,

        }
}
