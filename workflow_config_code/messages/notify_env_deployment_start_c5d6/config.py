"""
NotifyEnvDeploymentStartC5d6MessageConfig Configuration

Configuration data for the environment deployment start message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
🚀 We will start environment deployment if it's not yet deployed. This process will set up your Cyoda environment with the necessary configurations.

```mermaid
graph LR
    A([Finalize App Requirements]):::done e1@
    ==> B([Deploy Cyoda environment]):::done e2@
    ==> C([Gen Entities & Workflows]):::next
    C e3@ ==> D([Gen Controllers, Processors, Criteria & Tests]):::bar
    D e4@ ==> E([Launch Cyoda App]):::bar

    e2@{ animate: true }

    classDef bar stroke:#0D8484
    classDef done fill:#0D8484,stroke:#0D8484,color:#fff
    classDef next stroke:#0D8484,stroke-width:3px,stroke-dasharray:6 4
```

Please wait while we prepare your deployment environment...

"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
