"""
AskAboutApiD91fMessageConfig Configuration

Generated from config: workflow_configs/messages/ask_about_api_d91f/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """Would you like to improve or make adjustments to the functional requirements and the API?
Open to feedback if you’ve got any ideas — I’m all ears👂👂, well... sort of😏."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': True, 'publish': True}
