"""
InitSetupWorkflowJavaWorkflowConfig Workflow

Generated from config: workflow_configs/workflows/init_setup_workflow_java.json
Workflow configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class InitSetupWorkflowJavaWorkflowConfig:
    """Workflow configuration for init_setup_workflow_java"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this workflow"""
        return "init_setup_workflow_java"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get workflow configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
init_setup_workflow_java_workflow = InitSetupWorkflowJavaWorkflowConfig()
