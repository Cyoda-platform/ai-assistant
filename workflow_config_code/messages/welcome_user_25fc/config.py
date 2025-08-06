"""
WelcomeUser25fcMessageConfig Configuration

Generated from config: workflow_configs/messages/welcome_user_25fc/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """👋 Welcome to Cyoda Application Builder!
We’re excited to help you build your app — and just so you know, I’m a Cyoda app too, built with the same tools you’re about to use!

🔧 Process:

Define requirements & APIs

Build core logic prototype

Migrate to Cyoda backend (event-driven & production-ready)


👉 Learn more: https://cyoda.com

🚀 After that, you’ll get guidance on launching your app—and we can continue editing it as needed.

🌱 We're in alpha!
If something goes wrong or you have questions, reach out on [Discord](https://discord.gg/95rdAyBZr2) or click Restart workflows in the entities progress window.

Let’s build something great together!

```mermaid
graph TD
    A([Define & Confirm Functional Requirements]):::bar e1@== build_general_application.functional_requirements_specified
    ==> B([Build Sketch Prototype]):::bar
    B e2@== functional_requirements_generated ==> C([Validate Functionality & API Endpoints]):::bar
    C e3@== prototype_discussion_requested ==> D{Are You Happy With the Prototype?}:::bar
    D e4@== migration_confirmation_requested ==> E([Migrate to Cyoda Backend]):::bar
    E e5@== finished_app_generation_flow ==> F([Event-Driven Architecture + Non-Functional Requirements]):::bar
    F e6@== init_setup_workflow ==> G([Launch Your App]):::bar
    G e7@== edit_existing_workflow ==> H([Iterate & Edit as Needed]):::bar

    D e1@== No ==> B

    H e8@== locked_chat ==> I([Need Help? Click Retry or Ask on Discord]):::bar
    e1@{ animate: true }
    e2@{ animate: true }
    e3@{ animate: true }
    e4@{ animate: true }
    e5@{ animate: true }
    e6@{ animate: true }
    e7@{ animate: true }
    e8@{ animate: true }
    classDef bar stroke:#0f0
```"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
