"""
MigrationConfirmationNotifyD018MessageConfig Configuration

Generated from config: workflow_configs/messages/migration_confirmation_notify_d018/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """🚀 **Let’s generate your application code!**

I’ll take care of everything — no need to lift a finger.

⏳ While the code is being generated (~10 min), feel free to grab a coffee ☕ and relax.

**Here’s what’s happening behind the scenes:**
- **Entity Design:** Defining JSON structures for your entities (`application/entity/*`)
- **Workflow Design:** Mapping transitions (`application/workflow/*`)
- **Workflow Processor:** Java logic that powers it all (`application/processor/*`, `application/criterion/*`)

🛠️ This step brings your app to life — from requirements to real, running code.

✅ I’ll notify you as soon as everything’s ready to review.

Want to dive deeper into the concepts?
Check these out:
- [What’s an Entity Database?](https://medium.com/@paul_42036/whats-an-entity-database-11f8538b631a)
- [Entity Workflows for Event-Driven Architectures](https://medium.com/@paul_42036/entity-workflows-for-event-driven-architectures-4d491cf898a5)"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
