"""
NotifyControllerGeneratedD3e4MessageConfig Configuration

Configuration data for the notify controller generated message.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
✅ **REST API Controllers Generated Successfully**

The REST API controllers have been generated based on the workflow configurations and functional requirements.

📁 **Location:** `src/main/java/com/java_template/application/controller/`

🔄 **Next Step:** Generating business logic processors and validation criteria...
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
