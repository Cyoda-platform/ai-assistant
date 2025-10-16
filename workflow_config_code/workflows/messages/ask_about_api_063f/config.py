"""
AskAboutApi063fMessageConfig Configuration

Generated from config: workflow_configs/messages/ask_about_api_063f/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """Next up: functional requirements.
It will take me up to 10 mins to add requirements to `src/main/resources/functional_requirements/` directory.
I will add separate files for entities, workflows, processors, criteria and controllers.

Stay tuned — thoughtful thinking in progress. 🧠✨

"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
