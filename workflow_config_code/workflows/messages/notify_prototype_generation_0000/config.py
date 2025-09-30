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

```mermaid
%%{init: {'theme':'base','themeVariables':{
  'primaryColor':'#ECF8F8','primaryTextColor':'#083A3A','primaryBorderColor':'#0D8484',
  'lineColor':'#0D8484','fontFamily':'Inter, Arial, sans-serif','edgeLabelBackground':'#FFFFFF'
}}}%%
graph LR
    S((Start)):::start ==> A([🏆 Finalize App Requirements]):::done
    A e1@ ==> B([🛠️ Deploy Cyoda environment]):::done
    B e2@ ==> C([🏆 Gen Entities & Workflows]):::done
    C e3@ ==> D([🛠️ Gen Controllers, Processors, Criteria]):::next
    D e4@ ==> E([🔒 Launch Cyoda App]):::bar

    %% animate handoff to next step (D)
    e3@{ animate: true }

    classDef start fill:#FFFFFF,stroke:#0D8484,stroke-width:2px,color:#083A3A
    classDef bar   fill:#ECF8F8,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#083A3A
    classDef done  fill:#0D8484,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#FFFFFF
    classDef next  fill:#FFFFFF,stroke:#0D8484,stroke-width:3px,stroke-dasharray:6 4,rx:12,ry:12,color:#083A3A
    linkStyle default stroke:#0D8484,stroke-width:2px,opacity:0.95

```

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
