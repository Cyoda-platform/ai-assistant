"""
AskToConfirmMigration208eMessageConfig Configuration

Generated from config: workflow_configs/messages/ask_to_confirm_migration_208e/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """You’ve just built a working sketch of your Cyoda application. This marks the beginning of something powerful.

Next, you’ll convert this prototype into a full application that connects directly to your Cyoda Cloud environment.

By doing so, you gain:

✅ A robust, event-driven backend on a single, coherent platform

✅ Scalable, transactional architecture with far less complexity

✅ Clear, maintainable data models and workflows

✅ Enterprise-grade reliability, built in

✅ An ecosystem that accelerates delivery and adapts with your needs

👍 Let’s bring your prototype to life in the Cyoda Cloud."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': True, 'publish': True}
