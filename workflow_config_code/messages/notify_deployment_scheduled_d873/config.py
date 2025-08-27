"""
NotifyDeploymentScheduledD873MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_deployment_scheduled_d873/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """🚀 Your Cyoda environment deployment has been scheduled! The deployment process is now starting. Please wait while we set up your environment..."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
