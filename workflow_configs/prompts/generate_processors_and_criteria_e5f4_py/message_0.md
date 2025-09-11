
This project is a **Cyoda client application**.
Role & Objective

Develop and maintain a Cyoda client application by implementing entities, processors, criteria, and routers to spec and workflow definitions. Exit silently once all requirements pass and the project
quality check passes.

Golden Rules

-   No reflection.
-   Modify only the application directory.
-   Compile early and often; fix errors immediately.
-   Routes = thin proxies to EntityService (no business logic).
-   Prefer technical IDs for performance.
-   In processors, you cannot use entityService to update the current entity (read-only); The current entity will be updated automatically once you return from the processor.
    you may get/update/delete other entities via EntityService.
-   CRITICAL: Update using only manual transitions (never automatic).

Workflows — Super Important

Workflows define states and transitions for each entity:
- Saving an entity to a non-existent state (absent from workflow JSON) → fails.
- Update entities via manual transitions. Automatic transitions are not valid for update operations.
- Always cross-check with the workflow JSON in application/resources/workflow.

Repository Map

1.  Core APIs & Types
    -   common/service/entity_service.py
    -   common/entity/cyoda_entity.py
2.  Examples: example_application directory (processors, criteria, controllers)
CRITICAL: Check example_application before implementing your own.

3.  Functional Requirements
    -   Entities: application/resources/functional_requirements/entities.md
    -   Processors: application/resources/functional_requirements/processors.md
    -   Criteria: application/resources/functional_requirements/criteria.md
    -   Controllers: application/resources/functional_requirements/controllers.md
    -   Acceptance:
        application/resources/functional_requirements/user_requirement.md
4.  Workflow docs: application/resources/workflow/*.json

Implementation Checklist

1.  Familiarize with codebase in example_application directory.
2.  Entities
    -   Implement under application/entity/{entity_name}/version_1/ with Pydantic.

    -   Constants:

                ENTITY_NAME: ClassVar[str] = "ExampleEntity" -- always PascalCase
                ENTITY_VERSION: ClassVar[int] = 1 -- always 1

    
    Entities should exactly match the requirements specified in the application/resources/functional_requirements/entities.md file.
    Be careful with fields that semantically mean entity state (like status, state, etc.). If the functional requirements specify that we do not need business field for such field (status, state) then use entity state that you get from entity metadata. This state is managed by the workflow and you should not change it manually, you can only read it.
3.  Workflows
    -   Study JSON definitions (states + transitions) in resources/workflow/*.json.
    -   Use only manual transitions; if unsure → save without
        transition.
4.  Processors
    -   Implement under application/processor/.
    -   Study processors requirements in application/resources/functional_requirements/processors.md.
    -   No updates to current entity with the entityService - it will be updated automatically once you return; only get/update/delete other entities.
    -   To update another entity use entityService
    -   Apply correct transition (manual only), or omit for loop-back.
You can get entity id, state etc directly from entity as it extends CyodaEntity.
5.  Criteria
    -   Study criteria requirements in application/resources/functional_requirements/criteria.md.
    -   Implement under application/criterion/.
    -   Keep minimal and direct.
6.  Routers
    -   Study controller requirements in application/resources/functional_requirements/controllers.md.
    -   Implement under application/routes/.
    -   Endpoints must match requirements exactly; add CRUD if missing.
    -   Prefer technical IDs in responses.
    -   Update endpoints: transition nullable; must be manual if provided.
    -   Validate endpoints like in example_application routes. 
7.  Testing & Validation
    Validate with:
    python -m black .                    # Format code
    python -m isort .                    # Sort imports  
    python -m mypy .                     # Type checking
    python -m flake8 .                   # Style checking
    python -m bandit -r .                # Security scanning
    python -m pytest --cov              # Run tests with coverage
    look for more details in PACKAGE_MANAGEMENT_GUIDE.md

Acceptance Criteria

-   Entities/processors/criteria/routers fully match functional requirements.
-   Routes proxy only; no embedded business logic.
-   Code modifies only application directory.
-   Code passes quality checks.
-   Requirements in user_requirement.md satisfied.

Parallelise the work on processors, criteria and routers if possible.

Exit silently when all requirements are correctly implemented and build succeeds.

