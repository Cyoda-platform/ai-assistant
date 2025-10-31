"""
ScheduleDeployUserAppA3b7FunctionConfig Function

Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ScheduleDeployUserAppA3b7FunctionConfig(FunctionProcessor):
    """Function configuration for schedule_deploy_user_app_a3b7"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ScheduleDeployUserAppA3b7FunctionConfig.get_type()}.schedule_deploy_user_app_a3b7"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "schedule_deploy_user_app_a3b7"


# Create singleton instance
schedule_deploy_user_app_a3b7_function = ScheduleDeployUserAppA3b7FunctionConfig()

