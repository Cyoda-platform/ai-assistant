
### 
You are provided with a user requirement in `src/main/resources/functional_requirements/user_requirement.md` and `src/main/resources/functional_requirements/user_requirement_additional_info.md`.
Make sure you take in account all the information from src/main/resources/functional_requirements/user_requirement.md` and `src/main/resources/functional_requirements/user_requirement_additional_info.md`
There might be additional files in src/main/resources/functional_requirements directory. Read them all and take them into account.

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
    Keep the entity requirements as short as possible. Max 100 words per entity.
    
4. **Workflows**
   For each entity:
   4.1 * In the `functional_requirements` directory, create `<entity>/<entity>_workflow.md`.
   * Specify workflow states, transitions, and include a Mermaid state diagram.
   * Rules:
     * Each workflow must have an automatic transition from the initial state to the first state.
     * Loop transitions (to self or to a previous state) must be marked as manual.
     * Transitions can have **processors**, **criteria**, both, or none.
     * Do NOT complicate the workflow with complex criteria. Keep it simple unless the requirement explicitly calls for it.
     * Minimise the number of processors and criteria. One processor can do multiple things. Try to keep up to 3 processors per entity unless the requirement explicitly calls for more.
     * Keep the number of processors minimum to comply with the requirement. If the requirement is not explicit - minimize the number of processors.
     If the requirement i explicit - you must implement all the processors and criteria it requires.
     
  4.2 * For every processor: specify its name, entity, expected input, purpose, and expected output.
   * Provide **pseudocode for the `process()` method** (not Java).
   * If it updates another entity, reference the corresponding transition or mark as `null transition`.
   * Processor name should be in PascalCase.
     
   4.3 * For every criterion: specify its name
   * Provide **pseudocode for the `check()` method** (not Java).
   * Keep criteria simple: validity checks, permissions, state checks, etc.
   * Criterion name should be in PascalCase.
   
.  4.4 *CRITICAL*  **Workflow JSON**
   Add a valid workflow definition for this entity that contains ALL the states, transitions, processors and criteria exactly as specified in the workflow diagram:
   The name of the workflow must be the same as the entity name PascalCase. The number of processors and criteria in the workflow must match the number of processors and criteria in the workflow diagram exactly.
   * Path: `src/main/resources/workflow/<entityName>/version_1/<EntityName>.json` -- always `version_1`.
   * Validate each workflow against `llm_example/config/workflow/workflow_schema.json`.

8. **Controllers**
   For each entity, create `<entity>/<entity>_controllers.md` in `functional_requirements`.
   * Each entity should have its own controller (e.g., `UserController`, `OrderController`).
   * Endpoints:
     * Updates must accept a transition name (nullable if not moving states).
     * Transition names must align with the workflow definition.
   * Always provide **full request examples** (including all parameters) and **matching response examples**.
   * Verify that API specs match user requirements exactly.
    Keep controller requirements to a minimum. Max 100 words per controller.

9. ACCEPTANCE CRITERIA
    Once you are done with the above steps:
    
    Run FunctionalRequirementsValidator with ./gradlew validateFunctionalRequirements
    If it fails due to irrelevant reasons - run for each entity_workflow.md file individually with ./gradlew validateFunctionalRequirements -Pargs="src/main/resources/functional_requirements/myentity/myentity_workflow.md src/main/resources/workflow/myentity/version_1/MyEntity.json"  
    If there are missing processors or criteria - add them to the workflow JSON.
    
    Summary documentation added to src/main/resources directory of the project with the description of what you have done.


10. **Parallelization**
   Work on processors, criteria, and controllers in parallel once entity/workflow definitions are ready.

11. **Exit**

    Exit when all entities, workflows, processors, criteria, and controllers are defined.
    You must implement all the entities and related resources mentioned in the user requirement.
