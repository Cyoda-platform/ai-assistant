"""
ValidateAppQuality1b5cPromptConfig Configuration

Generated from config: workflow_configs/prompts/validate_app_quality_1b5c/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """You need to validate that entity processing logic has been successfully transferred from the prototype controller to processors and criteria, ensuring no logic duplication and that workflows make sense.

CONTEXT: During previous steps, we:
1. Analyzed EntityControllerPrototype code and identified business logic
2. Extracted entity processing logic and moved it to workflow processors and criteria
3. Created separate POJO entities based on the prototype
4. Generated workflows with processors for business operations
5. Created a Controller class that should only handle API routing and entity persistence

THIS IS A VALIDATION AND REFACTORING TASK: take action to correct things if necessary
Your job is to validate if the refactoring was successful and fix any issues found.

YOUR VALIDATION TASKS:
1. Read the prototype controller using get_file_contents: 'src/main/java/com/java_template/prototype/EntityControllerPrototype.java'
2. Read the current controller using get_file_contents: 'src/main/java/com/java_template/application/controller/Controller.java'
Notice that process code has been removed from the controller.
3. Use list_directory_files to examine what workflows, processors, and criteria were created:
   - 'src/main/java/com/java_template/application/workflow'
   - 'src/main/java/com/java_template/application/processor'
   - 'src/main/java/com/java_template/application/criterion'
5. Read each workflow, processor, and criteria files to understand what business logic was moved

VALIDATION CHECKS:
A. **Entity Processing Logic Migration Validation:**
   - Compare prototype controller business logic with processor implementations
   - Ensure complex entity processing operations were moved to processors. Not just left as placeholders or todos in processors.
   - Verify that processEntityName methods from prototype are properly implemented in processors
   - Check that processors follow the correct interface and naming conventions
   - Validate that entity transformation and business rules are in processors, not controller

B. **Controller Logic Duplication Check:**
   - Verify controller only contains API routing and entity persistence (entityService.addItem calls)
   - Ensure NO business logic remains in controller that should be in processors
   - Check that controller properly delegates to EntityService for persistence only
   - Validate that complex processing logic was completely removed from controller

C. **Criteria Implementation Validation:**
   - Verify criteria properly implement validation logic from prototype
   - Check that criteria follow the correct interface and naming conventions
   - Ensure criteria contain meaningful validation rules, not just placeholder code

D. **Workflow Logic Validation:**
   - Verify workflows make logical sense and follow proper state transitions
   - Check that workflow processors and criteria names match implemented classes
   - Ensure workflow states represent meaningful business processes
   - Validate that workflows properly orchestrate entity processing flow

CORRECTIVE ACTIONS (if validation fails):
List files that don't meet validation criteria:
- **Processors**: Rewrite if they don't properly implement entity processing logic from prototype
- **Criteria**: Rewrite if they don't properly implement validation logic from prototype
- **Controller**: Rewrite if it still contains business logic that should be in processors
- **Workflows**: Create missing processors or criteria identified by validate_workflow_implementation

VALIDATION SUCCESS CRITERIA:
- Entity processing logic is properly separated: complex business logic in processors, simple persistence in controller
- No logic duplication between controller and processors
- Workflows represent meaningful business processes and make logical sense
- All processors and criteria are properly implemented and follow naming conventions
- Controller is thin and only handles API routing + EntityService persistence calls

OUTPUT: Provide a detailed validation report with formal smileys. If everything is correct, confirm that the entity processing logic migration was successful and workflows make sense. If issues are found, outline them and formulate a prompt the user can give to their IDE AI assistant to fix the issues as. You cannot fix them yourself, return a prompt a user can use in their own IDE assistant."""
