"""
ScheduleDeployEnvF9edToolConfig Tool

Generated from config: workflow_configs/tools/schedule_deploy_env_f9ed/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ScheduleDeployEnvF9edToolConfig(FunctionProcessor):
    """Tool configuration for schedule_deploy_env_f9ed"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ScheduleDeployEnvF9edToolConfig.get_type()}.schedule_deploy_env_f9ed"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "schedule_deploy_env_f9ed"


# Create singleton instance
schedule_deploy_env_f9ed_tool = ScheduleDeployEnvF9edToolConfig()
