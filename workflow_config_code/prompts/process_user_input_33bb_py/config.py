"""
ProcessUserInput33bbPromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_33bb/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """**Troubleshooting:** Let the user know: missing or malformed values may cause runtime errors—ensure there are no stray spaces and quotes only where needed.
        
        If the user asks to fix some issue or do some improvements in the code:
Use 'list_directory_files' tool to list all the files in the project. 
List all files in 'application/entity' to get the list of entities.
List all files in 'application/processor' to get the list of processors.
List all files in 'application/criterion' to get the list of criteria.
List all files in 'application/resources/workflow' to get the list of workflow files.
List all files in 'application/routes' to get the list of controllers.

Use 'add_application_resource' tool to modify any file, passing the full path to the file starting with 'src' and the full content of the file as the second parameter.

Once the user is happy with the result or has no more questions, please call finish_discussion.
    """
