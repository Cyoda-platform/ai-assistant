"""
GenerateAppPromptConfig Prompt

Prompt configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class GenerateAppPythonPromptConfig:
    """Prompt configuration for generate app prompt"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this prompt"""
        return "generate_app_python_prompt"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> str:
        """Get prompt configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
generate_app_python_prompt = GenerateAppPythonPromptConfig()
