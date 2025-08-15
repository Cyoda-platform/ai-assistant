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
Please just ask the questions based on the requirement, use tools only if necessary.
Your response example:

Hello, thank you for your requirement! I will do my best to assist you.
Could you please help me clarify a few questions?
 Do I understand right that the main data models are: 
 What actions/operations would you like to perform on the data?
 Do you have any particular workflows in mind? (or discuss the provided ones)

User Requirement:

 """
