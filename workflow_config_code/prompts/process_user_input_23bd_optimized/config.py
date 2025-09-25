"""
ProcessUserInput23bdOptimizedPromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_23bd/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
Process user input. If the user asks a question, answer it. If the user provides a new requirement, extract it.
If the user asks for github access, use tool add_collaborator.
Ask the user if they would like to proceed with building their application or if they would like to add more detail.
Once the user confirms their requirement is complete you can call finish_discussion.
User Requirement:
"""
