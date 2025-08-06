"""
ChatBusinessEntityWorkflowConfig Workflow

Generated from config: workflow_configs/workflows/chat_business_entity.json
Workflow configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class ChatBusinessEntityWorkflowConfig:
    """Workflow configuration for chat_business_entity"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this workflow"""
        return "chat_business_entity"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get workflow configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
chat_business_entity_workflow = ChatBusinessEntityWorkflowConfig()
