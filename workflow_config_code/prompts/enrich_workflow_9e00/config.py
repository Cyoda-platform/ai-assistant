"""
EnrichWorkflow9e00PromptConfig Configuration

Generated from config: workflow_configs/prompts/enrich_workflow_9e00/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Return only valid JSON without any extra text without changes to the business logic. Please preserve original states order, it's an ordered dict."""
