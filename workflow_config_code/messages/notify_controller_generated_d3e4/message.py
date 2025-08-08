"""
NotifyControllerGeneratedD3e4MessageConfig Message

Implements MessageProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import MessageProcessor
from .config import get_config, get_meta_config


class NotifyControllerGeneratedD3e4MessageConfig(MessageProcessor):
    """Message configuration for notify_controller_generated_d3e4"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return MessageProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{NotifyControllerGeneratedD3e4MessageConfig.get_type()}.notify_controller_generated_d3e4"

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
notify_controller_generated_d3e4_message = NotifyControllerGeneratedD3e4MessageConfig()
