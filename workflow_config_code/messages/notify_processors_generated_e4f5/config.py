"""
NotifyProcessorsGeneratedE4f5MessageConfig Configuration

Configuration data for the notify processors generated message.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
✅ **Business Logic Processors and Criteria Generated Successfully**

The Cyoda processors and validation criteria have been generated based on the workflow configurations.

📁 **Locations:**
- Processors: `src/main/java/com/java_template/application/processor/`
- Criteria: `src/main/java/com/java_template/application/criteria/`

The generated components include:
- CyodaProcessor implementations for all workflow operations
- Business logic processing methods
- Entity validation criteria
- Error handling and logging
- Proper Spring annotations and dependency injection

🔄 **Next Step:** Compiling the complete project...
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
