"""
AskAboutApi063fMessageConfig Configuration

Generated from config: workflow_configs/messages/ask_about_api_063f/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """Next up: functional requirements.
Stay tuned — thoughtful thinking in progress. 🧠✨

```mermaid
graph LR
    A([Finalize App Requirements]):::done e1@
    ==> B([Deploy Cyoda environment]):::next
    B e2@ ==> C([Gen Entities & Workflows]):::bar
    C e3@ ==> D([Gen Controllers, Processors, Criteria & Tests]):::bar
    D e4@ ==> E([Launch Cyoda App]):::bar

    %% animate the transition to the next step
    e1@{ animate: true }

    classDef bar stroke:#0D8484
    classDef done fill:#0D8484,stroke:#0D8484,color:#fff
    classDef next stroke:#0D8484,stroke-width:3px,stroke-dasharray:6 4
```
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
