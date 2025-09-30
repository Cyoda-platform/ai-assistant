"""
ScheduleDeployEnvF9edFunctionConfig Function

Generated from config: workflow_configs/functions/schedule_deploy_env_f9ed/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ScheduleDeployEnvF9edFunctionConfig(FunctionProcessor):
    """Function configuration for schedule_deploy_env_f9ed"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ScheduleDeployEnvF9edFunctionConfig.get_type()}.schedule_deploy_env_f9ed"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "schedule_deploy_env_f9ed"


# Create singleton instance
schedule_deploy_env_f9ed_function = ScheduleDeployEnvF9edFunctionConfig()
