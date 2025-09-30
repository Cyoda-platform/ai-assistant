"""
NotifyControllerGeneratedD3e4MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_controller_generated_d3e4/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """✅ **REST API Controllers Generated Successfully**

The REST API controllers have been generated based on the workflow configurations and functional requirements.

📁 **Location:** `src/main/java/com/java_template/application/controller/`

🔄 **Next Step:** Generating business logic processors and validation criteria..."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
