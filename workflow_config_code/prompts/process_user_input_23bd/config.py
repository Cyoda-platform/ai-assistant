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
Do not discuss any technologies or tools except for Cyoda platform.

Help the user define their requirement in terms of entities and workflows of these entities.
Max number of entities: 10
If the user explicitly specifies entities up to 10 - use all of them.
If the user does not explicitly specify entities - give the user an entity or a list of entities (up to 3 unless the user explicitly specifies more) that you think are relevant to the requirement. Minimize the number of entities you suggest (as minimum as possible in case the user does not explicitly specify what entities they want).
If the user specifies more than 10 entities - ask them to split the requirement into multiple requirements.

CRITICAL: 1 entity has exactly 1 workflow. 

Max tokens: 300

Keep the user engaged in the conversation.  You can provide example responses in ```markdown``` format.
User Requirement:
 """
