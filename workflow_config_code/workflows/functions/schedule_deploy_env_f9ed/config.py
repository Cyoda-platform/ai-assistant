"""
ScheduleDeployEnvF9edFunctionConfig Configuration

Generated from config: workflow_configs/functions/schedule_deploy_env_f9ed/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "publish": True,
        "function": {
                "name": "schedule_deploy_env",
                "description": "Schedules deployment of Cyoda environment for the user",
                "strict": True
        }
}
