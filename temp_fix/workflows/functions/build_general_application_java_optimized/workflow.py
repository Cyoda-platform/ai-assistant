"""
BuildGeneralApplicationJavaWorkflowConfig Workflow

Generated from config: workflow_configs/workflows/build_general_application_java.json
Workflow configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class BuildGeneralApplicationJavaWorkflowConfig:
    """Workflow configuration for build_general_application_java"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this workflow"""
        return "build_general_application_java"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get workflow configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
build_general_application_java_workflow = BuildGeneralApplicationJavaWorkflowConfig()
