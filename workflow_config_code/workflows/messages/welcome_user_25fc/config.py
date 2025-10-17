"""
WelcomeUser25fcMessageConfig Configuration

Generated from config: workflow_configs/messages/welcome_user_25fc/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """👋 Welcome to Cyoda Application Builder! Let’s build something working together! We are going to go through the following steps:

🧐 Learn more about Cyoda on [Our website](https://cyoda.com) and [Docs](https://docs.cyoda.net)"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
