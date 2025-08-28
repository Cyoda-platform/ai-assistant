"""
NotifyRequirementDiscussionA1b3MessageConfig Configuration

Configuration data for the requirement discussion message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
💬 We are about to discuss your initial requirement. I'm going to give you my vision of the requirement and a couple of questions for clarification.

You don't have to answer all of them - I can use my own judgment to fill the gaps.

If you are ok with my vision you don't have to answer them at all, just click the Approve button and we'll go to the next step where I'll give you formal functional requirements that we can edit together or you can do it in your IDE.

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
