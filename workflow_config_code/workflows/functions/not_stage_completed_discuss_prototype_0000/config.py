"""
NotStageCompletedDiscussPrototype0000FunctionConfig Configuration

Generated from config: workflow_configs/functions/not_stage_completed_discuss_prototype_0000/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "not_stage_completed",
                "parameters": {
                        "transition": "discuss_prototype"
                }
        }
}
