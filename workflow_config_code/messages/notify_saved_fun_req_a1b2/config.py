"""
NotifySavedFunReqA1b2MessageConfig Configuration

Configuration data for the notify saved functional requirements message.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
✅ **Functional Requirements Saved Successfully**

📁 **Location:** `src/main/java/com/java_template/prototype/functional_requirement.md`

🔄 **Next Step:** Parsing workflow configurations from the functional requirements...
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
