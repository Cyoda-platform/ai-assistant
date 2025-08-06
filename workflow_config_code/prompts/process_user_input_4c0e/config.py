"""
ProcessUserInput4c0ePromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_4c0e/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Hello! Please do your best to help the user with just generated EntityControllerPrototype.java code.
 If the user asks you to make any improvements or fix any issues please first read the file 'src/main/java/com/java_template/prototype/EntityControllerPrototype.java' or 'src/main/java/com/java_template/application/entity/{EntityName}.java' to get the latest version.
 Then use your own judgement to introduce changes necessary for the user. Do not simply reuse the file content you read; always generate a new, modified version of the code that reflects the user's latest requests.
 Finally, make sure to save the file only after you have applied the required changes. Carefully verify that the updated content reflects your modifications, and do not proceed with saving unless actual updates have been made. Finally apply the necessary changes to the src/main/java/com/java_template/prototype/EntityControllerPrototype.java file. And let the user know what changes you introduced and why.
 If the user just asks any general question or a question about the code, read the EntityControllerPrototype.java file if necessary, answer the question, no save needed in this case.
 Call add_application_resource tool to save changes with the full contents of the file after your changes and the full path to the file.
 Path for the prototype: 'src/main/java/com/java_template/prototype/EntityControllerPrototype.java'
 Path for the entity: 'src/main/java/com/java_template/application/entity/{EntityName}.java'
 Call finish_discussion only once the user is happy with the result or asks to proceed."""
