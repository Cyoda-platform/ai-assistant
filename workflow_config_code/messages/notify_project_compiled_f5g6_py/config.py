"""
NotifyProjectCompiledF5g6MessageConfig Configuration

Configuration data for the notify project compiled message.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """
🎉 **Project Generation Completed Successfully!**

Your prototype application has been fully generated.


```mermaid
%%{init: {'theme':'base','themeVariables':{
  'primaryColor':'#ECF8F8','primaryTextColor':'#083A3A','primaryBorderColor':'#0D8484',
  'lineColor':'#0D8484','fontFamily':'Inter, Arial, sans-serif','edgeLabelBackground':'#FFFFFF'
}}}%%
graph LR
    S((Start)):::start ==> A([🏆 Finalize App Requirements]):::done
    A e1@ ==> B([🛠️ Deploy Cyoda environment]):::done
    B e2@ ==> C([🏆 Gen Entities & Workflows]):::done
    C e3@ ==> D([🛠️ Gen Controllers, Processors, Criteria & Tests]):::done
    D e4@ ==> E([🔒 Launch Cyoda App]):::bar

    %% animate handoff to next step (D)
    e3@{ animate: true }

    classDef start fill:#FFFFFF,stroke:#0D8484,stroke-width:2px,color:#083A3A
    classDef bar   fill:#ECF8F8,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#083A3A
    classDef done  fill:#0D8484,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#FFFFFF
    classDef next  fill:#FFFFFF,stroke:#0D8484,stroke-width:3px,stroke-dasharray:6 4,rx:12,ry:12,color:#083A3A
    linkStyle default stroke:#0D8484,stroke-width:2px,opacity:0.95

```



📁 **Project Structure:**
```
├── application/
│   ├── routes/     # REST API endpoints
│   ├── processor/      # Business logic
│   ├── criteria/       # Validation rules
│   └── entity/         # Entities  
│   └──resources/       # Configs

```
🚀 **Next Steps:**
You can run and test it locally or directly in **GitHub Codespaces**.

*Click Approve when you are ready to proceed and I will launch Cyoda setup assistant*

---### ✅ Approval or Feedback
If you're happy with the prototype, feel free to approve it.

If anything's off or you'd like changes, just ping me here. 🙌

Alternatively, you can use your IDE AI assistant with a suggested prompt:

**Prompt for your IDE:**

Complete AI startup guide can be found in *AI_TESTING_GUIDE.md*

If you make any changes, please share them with me in the chat or just push them to your branch and ask me to review them or just click "Approve".

Once you review the code and click *Approve*, I will launch the Cyoda setup assistant.
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': True, 'publish': True}
