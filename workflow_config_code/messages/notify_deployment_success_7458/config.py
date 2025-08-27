"""
NotifyDeploymentSuccess7458MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_deployment_success_7458/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """✅ Your [Cyoda environment](https://{build_namespace}.{client_host}) has been successfully deployed!

You can now proceed to setting up the application locally. Please let me know if you would like to add a new machine user to get oauth2 credentials."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': False, 'allow_anonymous_users': True}
