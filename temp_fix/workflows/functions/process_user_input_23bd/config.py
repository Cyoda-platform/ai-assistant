"""
ProcessUserInput23bdPromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_23bd/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """

Have a dialogue with the user to understand their needs and requirements.
We need to discuss only functionality and not the implementation details.
For example you can give examples of user stories and how the system should respond to them.
You can ask for specific APIs or just simply ask the user if there is anything else they want to add.
Do not discuss any technologies or tools except for Cyoda platform.
Let the user know if their requirement is complete and there is nothing else they want to add/discuss - they can just clink 'Approve' to move to the next step.

Max tokens: 300

Keep the user engaged in the conversation.  You can provide example responses in ```markdown``` format.
User Requirement:
 """
