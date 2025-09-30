"""
NotifyProcessorsGeneratedE4f5MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_processors_generated_e4f5/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """✅ **Business Logic Processors and Criteria Generated Successfully**

The Cyoda processors and validation criteria have been generated based on the workflow configurations.

📁 **Locations:**
- Processors: `src/main/java/com/java_template/application/processor/`
- Criteria: `src/main/java/com/java_template/application/criteria/`

🔄 **Next Step:** Enhancing the processors and generate tests. This will take several minutes. You'll get notification once it's done..."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
