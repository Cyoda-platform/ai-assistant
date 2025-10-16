"""
NotifyEnvDeploymentStartC5d6MessageConfig Configuration

Configuration data for the environment deployment start message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
🚀 We will start environment deployment if it's not yet deployed. 

This process will set up your Cyoda environment with the necessary configurations.

"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
