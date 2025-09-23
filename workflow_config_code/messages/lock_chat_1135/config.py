"""
LockChat1135MessageConfig Configuration

Generated from config: workflow_configs/messages/lock_chat_1135/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
    
🎉 Congrats on launching your app! 
    

```mermaid
%%{init: {'theme':'base','themeVariables':{
  'primaryColor':'#ECF8F8','primaryTextColor':'#083A3A','primaryBorderColor':'#0D8484',
  'lineColor':'#0D8484','fontFamily':'Inter, Arial, sans-serif','edgeLabelBackground':'#FFFFFF'
}}}%%
graph LR
    S((Start)):::start ==> A([🏆 Finalize App Requirements]):::done
    A e1@ ==> B([🏆 Deploy Cyoda environment]):::done
    B e2@ ==> C([🏆 Gen Entities & Workflows]):::done
    C e3@ ==> D([🏆 Gen Controllers, Processors, Criteria]):::done
    D e4@ ==> E([🏆 Launch Cyoda App]):::done

    classDef start fill:#FFFFFF,stroke:#0D8484,stroke-width:2px,color:#083A3A
    classDef bar   fill:#ECF8F8,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#083A3A
    classDef done  fill:#0D8484,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#FFFFFF
    classDef next  fill:#FFFFFF,stroke:#0D8484,stroke-width:3px,stroke-dasharray:6 4,rx:12,ry:12,color:#083A3A
    linkStyle default stroke:#0D8484,stroke-width:2px,opacity:0.95

```


Your hard work paid off—this is just the beginning. 

Keep iterating, stay creative, and aim high! 


🚀 Join our [Discord](https://discord.gg/95rdAyBZr2) to share feedback and stay updated. 🙌


"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': False, 'publish': True}
