"""
GenerateAppJavaPromptConfig Prompt

Generated from config: workflow_configs/agents/prompts/generate_app_java/message_0.md
Implements PromptConfig interface with get_name() and get_config() methods.
"""

from .config import get_config
from typing import Any, Dict


class GenerateAppJavaPromptConfig:
    """Prompt configuration for generate_app_java"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this prompt"""
        return "generate_app_java"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> str:
        """Get prompt configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
generate_app_java_prompt = GenerateAppJavaPromptConfig()
