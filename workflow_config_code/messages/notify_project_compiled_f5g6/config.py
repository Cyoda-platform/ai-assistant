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
src/main/java/com/java_template/
├── application/
│   ├── controller/     # REST API endpoints
│   ├── processor/      # Business logic
│   ├── criteria/       # Validation rules
│   └── entity/         # Entities
└── prototype/
    └── functional_requirement.md
    
src/main/resources/
└── workflow/           # Workflow configs
```

🚀 **Next Steps:**
You can run and test it locally or directly in **GitHub Codespaces**.

# Run the tests for processors and use debugger to step through the processors code
./gradlew test 

*Click Approve when you are ready to proceed and I will launch Cyoda setup assistant*
```

---### ✅ Approval or Feedback
If you're happy with the prototype, feel free to approve it.

If anything's off or you'd like changes, just ping me here. 🙌

Alternatively, you can use your IDE AI assistant with a suggested prompt:

**Prompt for your IDE:**
```markdown
This project is a **Cyoda client application**.

 * **Entities** (POJOs) are in `src/main/java/com/java_template/application/entity/`
 * **Workflows** (YAML/JSON configs) are in `src/main/resources/workflow/`
 * **Original user requirements** are in `src/main/java/com/java_template/prototype/user_requirement.md`
 * **Functional requirements** are in `src/main/java/com/java_template/prototype/functional_requirement.md`
 * **Controllers** (REST API endpoints) are in `src/main/java/com/java_template/application/controller/`
 * **Processors** (business logic) are in `src/main/java/com/java_template/application/processor/`
 * **Criteria** (validation rules) are in `src/main/java/com/java_template/application/criterion/`

 The system is **event-driven** — workflows define states, transitions, and criteria declaratively, without code changes.

 **Key rules:**

 1. Always review and learn from the original and functional requirement documents to fully understand the user requirements.
 2. If you update any entity or workflow, you must also update the functional requirement document.

 For detailed instructions, see `README.md` in the project root.
 The most up-to-date configuration and reference material can be loaded from the **doc server** at https://docs.cyoda.net.

Instructions:
1. Review the generated code and configuration. Fix any compilation errors.
2. Review the `prototype/functional_requirement.md` document. Make sure all the example requests and responses in the controllers are correct and up to date.
3. Review the `prototype/functional_requirement.md` document and Workflows (YAML/JSON configs). Make sure all processors and criteria are implemented correctly.
If any processors, criteria or controllers are not implemented correctly, fix the implementation.
Do not modify the workflow JSONs or entities without explicit approval.
4. Generate a report of the implemented functionality and if it matches the functional requirements.
```

If you make any changes, please share them with me in the chat or just push them to your branch and ask me to review them or just click "Approve".

Once you review the code and click *Approve*, I will launch the Cyoda setup assistant.
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': True, 'publish': True}
