"""
AskToDiscussPrototype983fMessageConfig Configuration

Generated from config: workflow_configs/messages/ask_to_discuss_prototype_983f/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """📽 **Your prototype is being generated**!

It’ll be ready in about 10 minutes ⏳. I’ll notify you as soon as it’s done.

In the meantime, feel free to switch to another task to make the most of your multitasking 🤩, or we can chat about something else.

Would you like me to tell you more about Cyoda?"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': False, 'publish': False}
