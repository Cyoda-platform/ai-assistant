"""
ProcessUserInput33bbPromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_33bb/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """**Troubleshooting:** Let the user know: missing or malformed values may cause runtime errors—ensure there are no stray spaces and quotes only where needed."""
