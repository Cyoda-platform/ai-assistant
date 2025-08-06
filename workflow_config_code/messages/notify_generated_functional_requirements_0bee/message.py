"""
NotifyGeneratedFunctionalRequirements0beeMessageConfig Message

Generated from config: workflow_configs/messages/notify_generated_functional_requirements_0bee/meta.json
Implements MessageProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import MessageProcessor
from .config import get_config, get_meta_config


class NotifyGeneratedFunctionalRequirements0beeMessageConfig(MessageProcessor):
    """Message configuration for notify_generated_functional_requirements_0bee"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return MessageProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{NotifyGeneratedFunctionalRequirements0beeMessageConfig.get_type()}.notify_generated_functional_requirements_0bee"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> str:
        """Get message configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_meta_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get message meta configuration"""
        meta_factory = get_meta_config()
        return meta_factory(params or {})


# Create singleton instance
notify_generated_functional_requirements_0bee_message = NotifyGeneratedFunctionalRequirements0beeMessageConfig()
