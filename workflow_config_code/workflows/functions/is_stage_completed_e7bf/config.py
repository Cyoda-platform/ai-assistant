"""
IsStageCompletedE7bfFunctionConfig Configuration

Generated from config: workflow_configs/functions/is_stage_completed_e7bf/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "is_stage_completed",
                "description": "Clones template repository",
                "parameters": {
                        "transition": "process_application_requirement"
                }
        }
}
