"""
ScheduleDeployUserAppA3b7FunctionConfig Configuration

Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "publish": True,
        "function": {
                "name": "schedule_deploy_user_application",
                "description": "Schedules deployment of user application",
                "strict": True
        }
}

