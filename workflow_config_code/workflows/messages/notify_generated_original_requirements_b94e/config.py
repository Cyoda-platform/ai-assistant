"""
NotifyGeneratedOriginalRequirementsB94eMessageConfig Configuration

Generated from config: workflow_configs/messages/notify_generated_original_requirements_b94e/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """✅  Saved original user requirements to `src/main/resources/functional_requirements/user_requirement.md`. Proceeding to the next step. You'll be notified soon....⏳😌"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
