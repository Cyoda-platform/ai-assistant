"""
NotifyCompilationStartedH8i9MessageConfig Configuration

Configuration data for the compilation started notification message.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
🧩 **Editing Started**
You'll be notified when editing is complete.
...
"""
def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}