"""
DeployUserAppWorkflowConfig Workflow

Workflow configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class DeployUserAppWorkflowConfig:
    """Workflow configuration for deploy_user_app"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this workflow"""
        return "deploy_user_app"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get workflow configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
deploy_user_app_workflow = DeployUserAppWorkflowConfig()

