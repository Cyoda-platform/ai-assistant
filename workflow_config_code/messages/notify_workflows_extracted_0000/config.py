"""
NotifyWorkflowsExtracted0000MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_workflows_extracted_0000/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """✅  Saved workflows to `src/main/java/com/java_template/application/workflow/*`. Continuing to generate the first prototype....⏳😌"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
