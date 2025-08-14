"""
EditGeneralApplicationJavaWorkflowConfig Workflow

Workflow configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class EditGeneralApplicationJavaWorkflowConfig:
    """Workflow configuration for edit_general_application_java"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this workflow"""
        return "edit_general_application_java"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get workflow configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
edit_general_application_java_workflow = EditGeneralApplicationJavaWorkflowConfig()
