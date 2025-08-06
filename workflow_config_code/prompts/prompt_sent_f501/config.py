"""
PromptSentF501PromptConfig Configuration

Generated from config: workflow_configs/prompts/prompt_sent_f501/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Let the user know: they should test their API by visiting `http://localhost:8000` (or their configured port) and ensure everything looks good.
- Let the user know: when they save `{entity_name}`, an event will be sent and processed by their workflow code in `application/processor/* and application/criterion/*`"""
