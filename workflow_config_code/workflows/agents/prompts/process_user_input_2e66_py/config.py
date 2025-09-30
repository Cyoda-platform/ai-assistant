"""
ProcessUserInput2e66PyPromptConfig Configuration

Generated from config: workflow_configs/agents/prompts/process_user_input_2e66_py/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Please, adjust the functional requirements according to the user request.

Functional requirements are located in application/resources/functional_requirements directory.
List the files and their contents to know the current state.
If the user asks to edit workflows - edit the files in application/resources/workflow directory. List the files and their contents to know the current state.

Use add_application_resource tool to add new files or save edited existing files.
Here is the user request:"""
