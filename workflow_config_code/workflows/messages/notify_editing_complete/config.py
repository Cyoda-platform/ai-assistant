"""
NotifyEditingCompleteMessageConfig Configuration

Generated from config: workflow_configs/messages/notify_editing_complete/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """✅ **Editing Complete**
Your application has been successfully edited and is ready for review."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': False, 'publish': True}
