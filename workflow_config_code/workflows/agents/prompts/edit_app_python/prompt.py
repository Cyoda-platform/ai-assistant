"""
EditAppPythonPromptConfig Prompt

Prompt configuration for editing existing Python applications.
"""

from .config import get_config
from typing import Any, Dict


class EditAppPythonPromptConfig:
    """Prompt configuration for edit_app_python"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this prompt"""
        return "edit_app_python"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> str:
        """Get prompt configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
edit_app_python_prompt = EditAppPythonPromptConfig()
