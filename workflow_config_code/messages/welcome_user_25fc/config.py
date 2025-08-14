"""
WelcomeUser25fcMessageConfig Configuration

Generated from config: workflow_configs/messages/welcome_user_25fc/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """\
👋 Welcome to Cyoda Application Builder! Let’s build something working together! We are going to go through the following steps:

```mermaid
graph TD
    A([Finalize App Requirements]):::bar e1@== build_general_application
    ==> B([Environment Deployment]):::bar
    B e2@== deploy_cyoda_env ==> C([Generate Entities&Workflows]):::bar
    C e3@== functional_requirements_to_prototype ==> D([Build Prototype]):::bar
    D e4@== init_setup_workflow ==> E([Launch Cyoda App]):::bar

    e1@{ animate: true }
    e2@{ animate: true }
    e3@{ animate: true }
    e4@{ animate: true }
    classDef bar stroke:#0D8484
```
   
   
🧐 Learn more about Cyoda on [Our website](https://cyoda.com) and [Docs](https://docs.cyoda.net)
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
