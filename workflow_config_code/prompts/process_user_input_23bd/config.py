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
```
User Requirement:
 """
