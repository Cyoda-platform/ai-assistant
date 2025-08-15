"""
ProcessUserInput23bdPromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_23bd/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """

Please help me get the information about the entities and workflows that can be used to design the application based on the user request.
Please limit the number of questions to 3, and provide example answers.

The goal is to understand the user's requirement and understand the entities and workflows that can be used to design the application.

Add a Ready-to-Copy section with an example user response in Markdown format.
```markdown
# Example Ready-to-Copy User Response
```
User Requirement:
 """
