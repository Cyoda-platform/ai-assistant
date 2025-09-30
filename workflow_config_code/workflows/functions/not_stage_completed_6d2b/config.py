"""
NotStageCompleted6d2bFunctionConfig Configuration

Generated from config: workflow_configs/functions/not_stage_completed_6d2b/function.json
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
                        "transition": "process_app_setup_4"
                }
        }
}
