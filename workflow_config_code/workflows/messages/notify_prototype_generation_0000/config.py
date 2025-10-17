"""
NotifyPrototypeGeneration0000MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_prototype_generation_0000/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """🌟 Let’s kick off the first prototype! 🛠️

We are going to generate Controllers, Processors, Criteria and Tests based on the functional requirements and entity class files!

💡 Want to dig deeper into the ideas behind this?  
- [What’s an Entity Database?](https://medium.com/@paul_42036/whats-an-entity-database-11f8538b631a)  
- [Entity Workflows for Event-Driven Architectures](https://medium.com/@paul_42036/entity-workflows-for-event-driven-architectures-4d491cf898a5)

Let’s make this prototype work smoothly together! 🚀

It’ll be ready in about 20 minutes ⏳. I’ll notify you as soon as it’s done.

🚧 Initial prototype is now in progress... 🚀💡"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
