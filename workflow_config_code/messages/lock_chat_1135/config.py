"""
LockChat1135MessageConfig Configuration

Generated from config: workflow_configs/messages/lock_chat_1135/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """🎉 Congrats on launching your first app! Your hard work paid off—this is just the beginning. Keep iterating, stay creative, and aim high! 🚀 Join our [Discord](https://discord.gg/95rdAyBZr2) to share feedback and stay updated. 🙌"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
