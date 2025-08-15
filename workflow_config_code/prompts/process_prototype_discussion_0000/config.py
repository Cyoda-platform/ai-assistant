"""
ProcessPrototypeDiscussion0000PromptConfig Configuration

Generated from config: workflow_configs/prompts/process_prototype_discussion_0000/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: \
"""Please, adjust the functional requirements, entities, workflows, controllers, processors and criteria according to the user request. 
Use 'list_directory_files' tool to list all the files in the project. 
List all files in 'src/main/java/com/java_template/application/entity' to get the list of entities.
List all files in 'src/main/java/com/java_template/application/processor' to get the list of processors.
List all files in 'src/main/java/com/java_template/application/criterion' to get the list of criteria.
List all files in 'src/main/resources/workflow' to get the list of workflow files.
List all files in 'src/main/java/com/java_template/application/controller' to get the list of controllers.

Use 'read_file' tool to read the content of any file. Pass the full path to the file as the parameter.

Use 'add_application_resource' tool to modify any file, passing the full path to the file starting with 'src' and the full content of the file as the second parameter.

Once the user is happy with the result or has no more questions, please call finish_discussion.
"""