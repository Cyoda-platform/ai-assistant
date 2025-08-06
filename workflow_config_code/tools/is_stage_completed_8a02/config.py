"""
IsStageCompleted8a02ToolConfig Configuration

Generated from config: workflow_configs/tools/is_stage_completed_8a02/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "is_stage_completed",
                "parameters": {
                        "transition": "discuss_api"
                }
        }
}
