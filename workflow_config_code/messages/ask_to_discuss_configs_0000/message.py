"""
AskToDiscussConfigs0000MessageConfig Message

Generated from config: workflow_configs/messages/ask_to_discuss_configs_0000/meta.json
Implements MessageProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import MessageProcessor
from .config import get_config, get_meta_config


class AskToDiscussConfigs0000MessageConfig(MessageProcessor):
    """Message configuration for ask_to_discuss_configs_0000"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return MessageProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{AskToDiscussConfigs0000MessageConfig.get_type()}.ask_to_discuss_configs_0000"

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
ask_to_discuss_configs_0000_message = AskToDiscussConfigs0000MessageConfig()
