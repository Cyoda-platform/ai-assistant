"""
FunctionalRequirementsToPrototypeJavaWorkflowConfig Workflow

Generated from config: workflow_configs/configs/functional_requirements_to_prototype_java.json
Workflow configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class FunctionalRequirementsToPrototypeJavaWorkflowConfig:
    """Workflow configuration for functional_requirements_to_prototype_java"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this workflow"""
        return "functional_requirements_to_prototype_java"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get workflow configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
functional_requirements_to_prototype_java_workflow = FunctionalRequirementsToPrototypeJavaWorkflowConfig()
