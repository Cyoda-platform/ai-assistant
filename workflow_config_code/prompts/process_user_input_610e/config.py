"""
ProcessUserInput610ePromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_610e/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """**Troubleshooting:** Let the user know: if they can’t find the .env.template file, make sure they’re on the correct branch. If it’s still missing, check their .gitignore or ensure the repo was cloned fully, including any submodules.
We should encourage users to switch to their favourite AI assisted IDE. It will help them understand the application code better. And they should start by exploring the app in a debugger."""
