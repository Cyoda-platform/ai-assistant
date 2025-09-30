"""
GenerateProcessorsAndCriteriaE5f4PromptConfig Configuration

Generated from config: workflow_configs/agents/prompts/generate_processors_and_criteria_e5f4/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """This project is a **Cyoda client application**.
Role & Objective

Develop and maintain a Cyoda client application by implementing entities, processors, criteria, and controllers to spec and workflow definitions. Exit once all requirements pass and the project
compiles.

Golden Rules

-   No reflection.
-   Do not modify anything in src/main/java/com/java_template/common.
-   Compile early and often; fix errors immediately.
-   Controllers = thin proxies to EntityService (no business logic).
-   Prefer technical IDs for performance.
-   In processors, you cannot update the current entity (read-only); you may get/update/delete other entities via EntityService.
-   CRITICAL: Update using only manual transitions (never automatic).

IDs & Metadata

-   Technical ID (UUID, unique, immutable):
    entityResponse.getMetadata().getId()
-   Entity state:
    entityResponse.getMetadata().getState()
    Entity state is managed by the workflow and you can not change it manually, you can only read it.
-   Business ID (user-defined, non-unique, mutable):
    retrievable/updatable with business ID–specific methods.
-   Update semantics:
    -   With transition → moves to that state.
    -   Without transition → loops back to same state.
    -   If in doubt, save without transition.

Workflows — Super Important

Workflows define states and transitions for each entity:
- Saving an entity to a non-existent state (absent from workflow JSON) →
fails.
- Update entities via manual transitions. Automatic transitions are not valid for update operations.
- Always cross-check with the workflow JSON in src/main/resources/workflow.

Repository Map

1.  Core APIs & Types
    -   common/service/EntityService.java
    -   common/workflow/CyodaEntity.java
    -   common/workflow/CyodaEventContext.java
2.  Examples: llm_example/code/application (processors, criteria, controllers)
CRITICAL: Check llm_example/code/application before implementing your own.

3.  Functional Requirements
    -   Entities: src/main/resources/functional_requirements/entityName/entityName.md
    -   Processors: src/main/resources/functional_requirements/entityName/entityName_workflow.md
    -   Criteria: src/main/resources/functional_requirements/entityName/entityName_workflow.md
    -   Controllers: src/main/resources/functional_requirements/entityName/entityName_controllers.md
    -   Acceptance:
        resources/functional_requirements/user_requirement.md
        All processors and criteria from src/main/resources/workflow/entityName/version_1/EntityName.json must be implemented.

Implementation Checklist - need to repeat for each entity defined in functional requirements.

0. Make sure build/generated-sources/js2p/org/cyoda/cloud/api/event generated classes are generated.
If not run ./gradlew build
1.  Familiarize with codebase in llm_example/code/application directory.
2.  Entities
    -   Implement POJOs under
        application/entity/{entity_name}/version_1/ with Lombok @Data.

    -   Constants:

            public static final String ENTITY_NAME = Entity.class.getSimpleName();
            public static final Integer ENTITY_VERSION = 1;

    -   Implement getModelKey() and isValid() as per template.
    
    Entities should exactly match the requirements specified in the src/main/resources/functional_requirements/entityName/entityName.md file.
    Be careful with fields that semantically mean entity state (like status, state, etc.). If the functional requirements specify that we do not need business field for such field (status, state) then use entity state that you get from entity metadata. This state is managed by the workflow and you should not change it manually, you can only read it.
3.  Workflows
    -   Study JSON definitions (states + transitions) in resources/workflow/*.json.
    -   Use only manual transitions for updates; if unsure → save without transition.
4.  Processors
    -   Study processors requirements in src/main/resources/functional_requirements/entityName/entityName_workflow.md .
    -   Entity passed to process(...) already contains all needed data.
    -   No updates to current entity - it will be updated automatically once you return; only get/update/delete other entities.
    -   To update another entity use entityService: apply correct transition (manual only), or omit for loop-back.
UUID currentEntityId = entityWithMetadata.metadata().getId(); -- if you need current entity technical id
String currentState = entityWithMetadata.metadata().getState(); -- if you need current entity state
5.  Criteria
    -   Study criteria requirements in src/main/resources/functional_requirements/entityName/entityName_workflow.md .
    -   Implement under application/criterion/.
    -   Keep minimal and direct.
6.  Controllers
    -   Study controller requirements in src/main/resources/functional_requirements/entityName/entityName_controllers.md.
    -   Implement under application/controller/.
    -   Accept entities as @RequestBody (not Map).
    -   Endpoints must match requirements exactly; add CRUD if missing.
    -   Prefer technical IDs in responses.
    -   Update endpoints: transition nullable; must be manual if provided.
7.  Testing & Validation
    -   Compile often with ./gradlew clean compileJava; resolve errors immediately.
    -   Validate against user_requirement.md.

Acceptance Criteria

-   Entities/processors/criteria/controllers fully match functional requirements and workflow JSON definitions.
-   The transitions in the code are consistent with the workflow JSON definitions.
-   Controllers proxy only; no embedded business logic.
-   No reflection; common untouched.
-   Project compiles cleanly.
-   Requirements in user_requirement.md satisfied.

    Once you are done with the above steps:
    
    Run WorkflowImplementationValidator with ./gradlew validateWorkflowImplementations
    If it fails due to irrelevant reasons - run for each entity_workflow.md file individually with ./gradlew validateWorkflowImplementations -Pargs="src/main/resources/workflow/myentity/version_1/MyEntity.json"  
    If there are missing processors or criteria - add them to the workflow JSON.
    
    Summary documenting what was implemented can be found in the project root directory.

Parallelize the work on different entities, processors, criteria, and controllers.
Each entity (with its workflow, processors, criteria, and controllers) can be treated as an independent subtask.
Plan the work so that all the entities are implemented in the end.  If it takes too much resources to implement all the entities in parallel, then use placeholders for processors, criteria and routers and implement them in separate tasks.

Exit when all entities with all requirements are correctly implemented and build succeeds."""
