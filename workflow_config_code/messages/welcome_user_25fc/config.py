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
    %% Nodes
    A([🔒 Finalize App Requirements]):::bar e1@== build_general_application
    ==> B([🔒 Deploy Cyoda environment]):::bar
    B e2@== deploy_cyoda_env ==> C([🔒 Gen Entities & Workflows]):::bar
    C e3@== functional_requirements_to_prototype ==> D([🔒 Gen Controllers, Processors, Criteria & Tests]):::bar
    D e4@== init_setup_workflow ==> E([🔒 Launch Cyoda App]):::bar

    %% Animations (original event markers)
    e1@{ animate: true }
    e2@{ animate: true }
    e3@{ animate: true }
    e4@{ animate: true }

    %% Styles (transparent nodes, teal accents)
    classDef bar fill:transparent,stroke:#0D8484,stroke-width:2px,rx:12,ry:12
    linkStyle default stroke:#0D8484,stroke-width:2px,opacity:0.95
```   
   
🧐 Learn more about Cyoda on [Our website](https://cyoda.com) and [Docs](https://docs.cyoda.net)
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
