"""
IsStageCompletedD5caFunctionConfig Configuration

Generated from config: workflow_configs/functions/is_stage_completed_d5ca/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "is_stage_completed",
                "parameters": {
                        "transition": "process_app_setup_3"
                }
        }
}
