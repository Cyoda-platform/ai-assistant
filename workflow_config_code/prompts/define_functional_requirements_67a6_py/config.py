"""
DefineFunctionalRequirements67a6PromptConfig Configuration

Generated from config: workflow_configs/prompts/define_functional_requirements_67a6/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
### 
You are provided with a user requirement in `application/resources/functional_requirements/user_requirement.md` (also check `application/resources/functional_requirements/user_requirement_additional_info.md` if it exists).
#### Instructions:
1. **Understand the user requirement.**
   Carefully read the user requirement files to extract the entities, workflows, and API needs.
2. **Review `README.md`**
   Make sure you understand the project structure before proceeding.
3. **Entities**
   For each entity found in the requirement:
   * In the `functional_requirements` directory, create a file named `<entity>/<entity>.md` (e.g., `user.md`, `order.md`).
   * Document the entity’s detailed requirements: name, attributes, and relationships with other entities.
   * Remember: *entity state* is internal (`entity.meta.state`) and should **not** appear in the entity schema. If requirements mention “state” or “status”, map them to `entity.meta.state` instead and explain this to the user.
    Max 10 entities
    
4. **Workflows**
   For each entity:
   4.1 * In the `functional_requirements` directory, create `<entity>/<entity>_workflow.md`.
   * Specify workflow states, transitions, and include a Mermaid state diagram.
   * Rules:
     * Each workflow must have an automatic transition from the initial state to the first state.
     * Loop transitions (to self or to a previous state) must be marked as manual.
     * Transitions can have **processors**, **criteria**, both, or none.
     * Do NOT complicate the workflow with complex criteria. Keep it simple unless the requirement explicitly calls for it.
     * Keep the number of processors minimum to comply with the requirement. If the requirement is not explicit - minimize the number of processors.
     If the requirement i explicit - you must implement all the processors and criteria it requires.
     
  4.2 * For every processor: specify its name, entity, expected input, purpose, and expected output.
   * Provide **pseudocode for the `process()` method** (not Java).
   * If it updates another entity, reference the corresponding transition or mark as `null transition`.
     
   4.3 * For every criterion: specify its name
   * Provide **pseudocode for the `check()` method** (not Java).
   * Keep criteria simple: validity checks, permissions, state checks, etc.
   
.  4.4 *CRITICAL*  **Workflow JSON**
   Add a valid workflow definition for this entity that contains ALL the states, transitions, processors and criteria exactly as specified in the workflow diagram:
   The name of the workflow must be the same as the entity name PascalCase. The number of processors and criteria in the workflow must match the number of processors and criteria in the workflow diagram exactly.
   * Path: `application/resources/workflow/<entityName>/version_1/<EntityName>.json` -- always `version_1`.
   * Validate each workflow against `example_application/resources/workflow/workflow_schema.json`.

8. **Controllers**
   For each entity, create `<entity>/<entity>_controllers.md` in `functional_requirements`.
   * Each entity should have its own controller (e.g., `UserController`, `OrderController`).
   * Endpoints:
     * Updates must accept a transition name (nullable if not moving states).
     * Transition names must align with the workflow definition.
   * Always provide **full request examples** (including all parameters) and **matching response examples**.
   * Verify that API specs match user requirements exactly.

9. **Parallelization**
   Work on processors, criteria, and controllers in parallel once entity/workflow definitions are ready.

10. **Exit**
    When all per-entity requirements are implemented correctly, exit.
    
"""
