"""
NotifyDeploymentRollbackC4f9MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_deployment_rollback_c4f9/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """🙈  We encountered internal issues with checking the status of your Cyoda environment. You can check the the deployment status for {build_id} manually here or in any chat. Don't worry!"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True, 'allow_anonymous_users': True}
