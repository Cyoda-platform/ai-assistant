"""
DeployCyodaEnvWorkflowConfig Workflow

Generated from config: workflow_configs/configs/deploy_cyoda_env.json
Workflow configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class DeployCyodaEnvWorkflowConfig:
    """Workflow configuration for deploy_cyoda_env"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this workflow"""
        return "deploy_cyoda_env"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get workflow configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
deploy_cyoda_env_workflow = DeployCyodaEnvWorkflowConfig()
