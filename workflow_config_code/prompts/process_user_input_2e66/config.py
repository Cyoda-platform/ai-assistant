"""
ProcessUserInput2e66PromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_2e66/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Please, adjust the functional requirements and the API according to the user request.

Functional requirements are located in src/main/resources/functional_requirements directory. List the files and their contents to know the current state.
 * **Workflows** (YAML/JSON configs) are in `src/main/resources/workflow/entityName/version_1/`
 * **Original user requirements** are in `src/main/resources/functional_requirements/user_requirement.md`
 * **Functional requirements** are in `src/main/java/com/java_template/prototype/functional_requirement.md`

Here is the user request:"""
