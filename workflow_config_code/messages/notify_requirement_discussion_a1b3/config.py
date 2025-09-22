"""
NotifyRequirementDiscussionA1b3MessageConfig Configuration

Configuration data for the requirement discussion message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
💬 Let’s review your initial requirement.
I’ll share my understanding (my “vision”) and a few clarifying questions.

You can answer as many as you like—I’ll use good judgment to fill any gaps.

If everything looks right, just click Approve. We’ll move to the next step, where I’ll provide formal functional requirements for us to edit together here—or you can work on them in your IDE.

```mermaid
%%{init: {'theme':'base','themeVariables':{
  'primaryColor':'#ECF8F8','primaryTextColor':'#083A3A','primaryBorderColor':'#0D8484',
  'lineColor':'#0D8484','fontFamily':'Inter, Arial, sans-serif','edgeLabelBackground':'#FFFFFF'
}}}%%
graph LR
    S((Start)):::start e0@ ==> A([🛠️ Finalize App Requirements]):::next
    A e1@ ==> B([🔒 Deploy Cyoda environment]):::bar
    B e2@ ==> C([🔒 Gen Entities & Workflows]):::bar
    C e3@ ==> D([🔒 Gen Controllers, Processors, Criteria]):::bar
    D e4@ ==> E([🔒 Launch Cyoda App]):::bar

    %% animate incoming to the next step (A)
    e0@{ animate: true }

    classDef start fill:#FFFFFF,stroke:#0D8484,stroke-width:2px,color:#083A3A
    classDef bar   fill:#ECF8F8,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#083A3A
    classDef done  fill:#0D8484,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#FFFFFF
    classDef next  fill:#FFFFFF,stroke:#0D8484,stroke-width:3px,stroke-dasharray:6 4,rx:12,ry:12,color:#083A3A
    linkStyle default stroke:#0D8484,stroke-width:2px,opacity:0.95

```


"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'notification', 'approve': False, 'publish': True}
