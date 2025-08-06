"""
NotStageCompletedD1b6ToolConfig Configuration

Generated from config: workflow_configs/tools/not_stage_completed_d1b6/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "not_stage_completed",
                "parameters": {
                        "transition": "process_app_setup_1"
                }
        }
}
