"""
AskAboutApi063fPyMessageConfig Message

Generated from config: workflow_configs/messages/ask_about_api_063f_py/meta.json
Implements MessageProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import MessageProcessor
from .config import get_config, get_meta_config


class AskAboutApi063fPyMessageConfig(MessageProcessor):
    """Message configuration for ask_about_api_063f_py"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return MessageProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{AskAboutApi063fPyMessageConfig.get_type()}.ask_about_api_063f_py"

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
ask_about_api_063f_py_message = AskAboutApi063fPyMessageConfig()
