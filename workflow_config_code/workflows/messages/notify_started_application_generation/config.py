"""
NotifyStartedApplicationGenerationMessageConfig Configuration

Generated from config: workflow_configs/messages/notify_started_application_generation/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """Let's proceed to the next step: checking the status of your Cyoda environment.

Once we confirm the environment is ready or is being deployed, we'll move on to building your application."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
