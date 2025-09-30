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

✅ Approval or Feedback

If you're happy with the prototype, feel free to approve it.

If anything's off or you'd like changes, just ping me here. 🙌

Alternatively, you can use your IDE AI assistant with a suggested prompt:

**Prompt for your IDE:**

```markdown

This project is a **Cyoda client application**.
Your role is to **validate** that entities, processors, criteria, and routers are correctly implemented according to the functional requirements and workflow definitions.
Do **not generate or re-implement code** — focus on **reviewing, checking, and highlighting inconsistencies or missing pieces**.

#### Validation Objectives

* Confirm all requirements are fully implemented and consistent.
* Ensure workflows, processors, criteria, and routers match the functional requirements and workflow JSONs.
* Verify that the code passes all quality checks.
* Exit once all validations succeed.

#### Workflows — Validation Focus

* Updates use manual transitions only.
* No invalid states (must exist in workflow JSON).
* Cross-check with JSON in `application/resources/workflow`.

#### Repository Map — Cross-Check Against

1. **Core APIs & Types** → `common/service/entity_service.py`, `common/entity/cyoda_entity.py`.
2. **Examples** → `example_application/`.
3. **Functional Requirements** → `application/resources/functional_requirements/*`.
4. **Workflow JSONs** → `application/resources/workflow/*.json`.

#### Validation Checklist (Per Entity)
1. **Entities** – Implemented under `application/entity/{entity}/version_1/`.
   * Fields match `entityName.md` from functional requirements.
   * Constants (`ENTITY_NAME`, `ENTITY_VERSION`) correct.
2. **Workflows** – States and transitions align with JSON.
3. **Processors** – Match requirements in `entity_workflow.md`.
   * No updates to current entity.
   * Correct use of `entityService` for others.
   * No kwargs; only entity argument.
   * No validation of entity state.
4. **Criteria** – Minimal, accurate, direct.
5. **Routers** – Match requirements in `entityName_routes.md`.
   * Endpoints exactly as specified.
   * Technical IDs in responses.
   * Properly registered in `app.py` (check against `example_application`).
6. **Testing & Validation** –
   * No `__init__.py` in project root.
   * Run quality checks:

     ```bash
     python -m black .
     python -m isort .
     python -m mypy .
     python -m flake8 .
     ```

#### Acceptance Criteria

* Entities, processors, criteria, and routers match functional requirements.
* Routes act as proxies only.
* Code modifies only the `application` directory.
* Project passes all quality checks.
* Requirements in `user_requirement.md` are satisfied.
* Criteria remain minimal and direct.

**Exit when**: all entities, workflows, processors, criteria, and routers validate successfully and the project passes quality checks.
```
"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {'type': 'question', 'approve': True, 'publish': True}
