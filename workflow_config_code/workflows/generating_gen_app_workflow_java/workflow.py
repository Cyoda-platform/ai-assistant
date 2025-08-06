"""
GeneratingGenAppWorkflowJavaWorkflowConfig Workflow

Generated from config: workflow_configs/workflows/generating_gen_app_workflow_java.json
Workflow configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class GeneratingGenAppWorkflowJavaWorkflowConfig:
    """Workflow configuration for generating_gen_app_workflow_java"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this workflow"""
        return "generating_gen_app_workflow_java"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get workflow configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
generating_gen_app_workflow_java_workflow = GeneratingGenAppWorkflowJavaWorkflowConfig()
