"""
AskToDiscussConfigs0000MessageConfig Configuration

Generated from config: workflow_configs/messages/ask_to_discuss_configs_0000/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: \
"""

```mermaid
%%{init: {'theme':'base','themeVariables':{
  'primaryColor':'#ECF8F8','primaryTextColor':'#083A3A','primaryBorderColor':'#0D8484',
  'lineColor':'#0D8484','fontFamily':'Inter, Arial, sans-serif','edgeLabelBackground':'#FFFFFF'
}}}%%
graph LR
    S((Start)):::start ==> A([🏆 Finalize App Requirements]):::done
    A e1@ ==> B([🛠️ Deploy Cyoda environment]):::done
    B e2@ ==> C([🛠️ Gen Entities & Workflows]):::done
    C e3@ ==> D([🔒 Gen Controllers, Processors, Criteria & Tests]):::bar
    D e4@ ==> E([🔒 Launch Cyoda App]):::bar

    classDef start fill:#FFFFFF,stroke:#0D8484,stroke-width:2px,color:#083A3A
    classDef bar   fill:#ECF8F8,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#083A3A
    classDef done  fill:#0D8484,stroke:#0D8484,stroke-width:2px,rx:12,ry:12,color:#FFFFFF
    classDef next  fill:#FFFFFF,stroke:#0D8484,stroke-width:3px,stroke-dasharray:6 4,rx:12,ry:12,color:#083A3A
    linkStyle default stroke:#0D8484,stroke-width:2px,opacity:0.95

```

✅ **Entity POJOs** and **workflow configurations** have been added to your application.
   📂 src/
    ├─ main/java/com/java_template/application/entity/entityName/version_1    ← Entities
    └─ main/resources/workflow/entityName/version_1                           ← Workflows

For a detailed reference on workflow configuration, see the **[Cyoda Workflow Configuration Guide](https://docs.cyoda.net/#guides/workflow-config-guide)**. It explains:

• How to define states, transitions, and criteria  
• Manual vs automated transitions  
• Processor execution modes and best practices  
• Example workflows like "Payment Request Workflow" for real-world scenarios

You can preview workflows visually in the **“Open canvas”** view (upper-right corner of the UI).

Please review the generated entities and workflows in your `{git_branch}` branch.

🔗 [Cyoda GitHub](https://github.com/Cyoda-platform/{repository_name}/tree/{git_branch})

I can assist with any changes or questions.
 
Alternatively, you can edit configs directly in the code.

If you need to push changes to your branch, ask me here for access. I'll need your GitHub username to add you as a collaborator. If you'd like to be a Cyoda contributor instead of a contributor and enjoy more privileges, please let us know via [Discord](https://discord.gg/95rdAyBZr2).

You can evolve the workflows and entities in your IDE with your own IDE assistant.

**Prompt for your IDE:**

```markdown
This project is a **Cyoda client application**.

 * **Entities** (POJOs) are in `src/main/java/com/java_template/application/entity/entityName/version_1/`
 * **Workflows** (YAML/JSON configs) are in `src/main/resources/workflow/entityName/version_1/`
 * **Original user requirements** are in `src/main/java/com/java_template/prototype/user_requirement.md`
 * **Functional requirements** are in `src/main/java/com/java_template/prototype/functional_requirement.md`

 The system is **event-driven** — workflows define states, transitions, and criteria declaratively, without code changes.

 **Key rules:**

 1. Always review and learn from the original and functional requirement documents to fully understand the user requirements.
 2. If you update any entity or workflow, you must also update the functional requirement document.

 For detailed instructions, see `README.md` in the project root.
 The most up-to-date configuration and reference material can be loaded from the **doc server** at https://docs.cyoda.net.
 Assist in locating, editing, and creating entities and workflows, explaining configuration concepts, and applying best practices from the Cyoda Workflow Configuration Guide.
```

If you make any changes, please share them with me in the chat or just push them to your branch and ask me to review them or just click "Approve".
"""



def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': True, 'publish': True}
