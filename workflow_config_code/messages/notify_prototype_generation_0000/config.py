"""
NotifyPrototypeGeneration0f5bMessageConfig Configuration

Generated from config: workflow_configs/messages/notify_prototype_generation_0f5b/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: \
"""
🌟 Let’s kick off the first prototype! 🛠️

💡  Just a heads-up: this prototype is a **simulation of the application**.
- No Cyoda components will be running.
- No data persistence.
- The goal is to confirm the **business logic** and ensure you’re getting the expected results.

For now, please focus on:
✅ API endpoints and functional requirements  
✅ Simulated state machine behavior  
✅ Integrating with any external APIs (a perfect time to test these out!)

We’re not tackling non-functional requirements yet—this stage is all about getting the prototype right.

💡 Want to dig deeper into the ideas behind this?  
- [What’s an Entity Database?](https://medium.com/@paul_42036/whats-an-entity-database-11f8538b631a)  
- [Entity Workflows for Event-Driven Architectures](https://medium.com/@paul_42036/entity-workflows-for-event-driven-architectures-4d491cf898a5)

Let’s make this prototype work smoothly together! 🚀

It’ll be ready in about 5 minutes ⏳. I’ll notify you as soon as it’s done.

🚧 Initial prototype is now in progress... 🚀💡
"""

def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
