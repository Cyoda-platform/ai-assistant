"""
NotifyProjectCompiledF5g6MessageConfig Configuration

Generated from config: workflow_configs/messages/notify_project_compiled_f5g6/meta.json
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """🎉 **Project Generation Completed Successfully!**

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
    C e3@ ==> D([🛠️ Gen Controllers, Processors, Criteria]):::done
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

    
src/main/resources/
└── workflow/           # Workflow configs
```

🚀 **Next Steps:**
You can run and test it locally or directly in **GitHub Codespaces**.

Run the tests for processors and use debugger to step through the processors code

./gradlew test 

*Click Approve when you are ready to proceed and I will launch Cyoda setup assistant*

 ✅ Approval or Feedback
If you're happy with the prototype, feel free to approve it.

If anything's off or you'd like changes, just ping me here. 🙌

Alternatively, you can use your IDE AI assistant with a suggested prompt:

**Prompt for your IDE:**

```markdown

This project is a **Cyoda client application**.
Your role is to **validate** that entities, processors, criteria, controllers, and workflows are correctly implemented according to the functional requirements and workflow definitions.
Do **not** generate new code — focus on **reviewing, checking, and highlighting issues or inconsistencies**.

#### Validation Objectives
* Confirm implementation matches requirements and workflow definitions.
* Ensure the project compiles and validators pass.
* Exit once all checks succeed and requirements are met.

#### Golden Rules — Check For
* Processors do not update the current entity (read-only) via entityService update operations.
* Only manual transitions allowed for updates.

#### IDs & Metadata — Verify Correct Usage

* **Technical ID (UUID, immutable)** → `entityResponse.getMetadata().getId()`
* **Entity state (workflow-managed)** → `entityResponse.getMetadata().getState()` (read-only)
* **Business ID (mutable, user-defined)** → must be handled correctly.
* **Update semantics:**

  * With transition → moves to new state
  * Without transition → loops to same state
  * If unclear → save without transition

#### Workflows — Critical Validation

* Entity updates use **manual transitions only**.
* No invalid saves to states absent from workflow JSON.
* JSON in `src/main/resources/workflow` matches implemented transitions.

#### Repository Map — Cross-Check Against

1. **Core APIs & Types** → `EntityService`, `CyodaEntity`, `CyodaEventContext`.
2. **Examples** → `llm_example/code/application`.
3. **Functional Requirements** → `functional_requirements/*`.
4. **Workflow JSONs** → `workflow/<entityName>/version_1/`.

#### Validation Checklist (Per Entity)

0. Confirm generated classes exist under `build/generated-sources/js2p/...`.
1. **Entities** – POJOs match `entityName.md`.
2. **Workflows** – States + transitions align with JSON.
3. **Processors** – Match `entity_workflow.md`.

   * No updates to current entity via entityService update operations.
   * Proper `EntityService` use.
   * Correct transitions.
4. **Criteria** – Minimal, accurate, per requirements.
5. **Controllers** – Endpoints match specs exactly.

6. **Validation** – Project compiles (`./gradlew clean compileJava`).

   * `./gradlew validateWorkflowImplementations` passes.

#### Acceptance Criteria

* Implementation matches functional requirements and workflow JSON exactly.
* Transitions align with workflow JSON.
* `user_requirement.md` requirements fully satisfied.

If validation fails:
* Run per-entity validation:
  ```bash
  ./gradlew validateWorkflowImplementations -Pargs="src/main/resources/workflow/myentity/version_1/MyEntity.json"
  ```
* Identify missing or incorrect processors/criteria.

**Exit when**: all entities, workflows, processors, criteria, and controllers validate successfully and build compiles clean."""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': True, 'publish': True}
