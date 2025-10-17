"""
NotifyEnvDeploymentStartC5d6MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_env_deployment_start_c5d6/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """🚀 We will start environment deployment if it's not yet deployed. 

This process will set up your Cyoda environment with the necessary configurations."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
