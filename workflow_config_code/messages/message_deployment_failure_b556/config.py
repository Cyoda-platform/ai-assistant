"""
MessageDeploymentFailureB556MessageConfig Configuration

Generated from config: workflow_configs/messages/message_deployment_failure_b556/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """⚠️ Sorry, we encountered internal issues while deploying your Cyoda environment.

Our team has been notified and is looking into it. Please try again shortly, or reach out if the issue persists. You can proceed with the current chat."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': False, 'publish': True, 'allow_anonymous_users': True}
