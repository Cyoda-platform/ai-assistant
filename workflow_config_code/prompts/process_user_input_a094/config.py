"""
ProcessUserInputA094PromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_a094/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """**Troubleshooting:** Let the user know: if the import fails, they should verify their JSON formats and version compatibility, and check the Cloud logs for detailed import errors."""
