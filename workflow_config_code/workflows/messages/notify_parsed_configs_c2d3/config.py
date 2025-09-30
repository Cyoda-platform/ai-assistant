"""
NotifyParsedConfigsC2d3MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_parsed_configs_c2d3/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """✅ **Workflow Orchestrators Generated Successfully**

The workflow JSON files have been analyzed and Java workflow orchestrators have been generated with conditional logic.

📁 **Locations:**
- Workflow JSONs: `src/main/resources/workflow`
- Orchestrators: `src/main/java/com/java_template/application/orchestrator/`

The generated orchestrators include:
- Conditional logic for workflow transitions
- Processor factory integration
- Criteria factory integration
- State management and transition handling
- Proper error handling and logging

🔄 **Next Step:** Generating REST API controllers..."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
