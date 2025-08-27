"""
ScheduleCloseProcessB2b5ToolConfig Configuration

Generated from config: workflow_configs/tools/schedule_close_process_b2b5/tool.json
Configuration data for the scheduled processor.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get scheduled processor configuration factory"""
    return lambda params=None: {
        "type": "scheduled",
        "name": "schedule_close_process",
        "config": {
            "delayMs": 30000,
            "timeoutMs": 3600000,
            "transition": "check_status"
        }
    }
