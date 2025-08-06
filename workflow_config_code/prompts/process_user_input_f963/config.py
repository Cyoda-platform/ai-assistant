"""
ProcessUserInputF963PromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_f963/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """**Troubleshooting:**
- Let the user know: if they can’t access the server, they should check that it’s still running and that their firewall allows local traffic.
- Let the user know: if no GRPC event occurs, they should verify their endpoint triggers GRPC and inspect the logs to trace payload delivery.
We should encourage users to switch to their favourite AI assisted IDE. It will help them understand the application code better. And they should start by exploring the app in a debugger."""
