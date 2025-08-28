"""
ScheduleDeployEnvF9edToolConfig Configuration

Generated from config: workflow_configs/tools/schedule_deploy_env_f9ed/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "publish": True,
        "function": {
                "name": "schedule_deploy_env",
                "description": "Schedules deployment of Cyoda environment for the user",
                "strict": True

        }
}
