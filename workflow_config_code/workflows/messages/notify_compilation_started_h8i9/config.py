"""
NotifyCompilationStartedH8i9MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_compilation_started_h8i9/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """🧩 **Compilation Started**

The GitHub Actions compilation workflow has been triggered.

Proceeding to process compilation results and apply any necessary fixes🔧..."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
