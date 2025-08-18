"""
NotifyGeneratedFunctionalRequirements0beeMessageConfig Configuration

Generated from config: workflow_configs/messages/notify_generated_functional_requirements_0bee/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """✅  Saved functional requirements to `src/main/java/com/java_template/prototype/functional_requirement.md`. Proceeding to entities generation....⏳😌"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
