"""
GenerateOriginalRequirements52efPromptConfig Configuration

Generated from config: workflow_configs/agents/prompts/generate_original_requirements_52ef/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Please return exactly what the user asked for."""
