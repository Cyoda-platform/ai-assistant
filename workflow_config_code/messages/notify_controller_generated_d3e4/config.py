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

The generated controllers include:
- CRUD endpoints for all entities
- Request/response DTOs
- Proper validation and error handling
- Cross-origin resource sharing (CORS) configuration
- RESTful API design patterns

🔄 **Next Step:** Generating business logic processors and validation criteria...
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
