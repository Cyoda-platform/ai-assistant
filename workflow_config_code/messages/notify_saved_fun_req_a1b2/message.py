"""
NotifySavedFunReqA1b2MessageConfig Message

Implements MessageProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import MessageProcessor
from .config import get_config, get_meta_config


class NotifySavedFunReqA1b2MessageConfig(MessageProcessor):
    """Message configuration for notify_saved_fun_req_a1b2"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return MessageProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{NotifySavedFunReqA1b2MessageConfig.get_type()}.notify_saved_fun_req_a1b2"

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
notify_saved_fun_req_a1b2_message = NotifySavedFunReqA1b2MessageConfig()
