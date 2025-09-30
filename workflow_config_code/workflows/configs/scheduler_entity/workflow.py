"""
SchedulerEntityWorkflowConfig Workflow

Generated from config: workflow_configs/configs/scheduler_entity.json
Workflow configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class SchedulerEntityWorkflowConfig:
    """Workflow configuration for scheduler_entity"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this workflow"""
        return "scheduler_entity"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get workflow configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
scheduler_entity_workflow = SchedulerEntityWorkflowConfig()
