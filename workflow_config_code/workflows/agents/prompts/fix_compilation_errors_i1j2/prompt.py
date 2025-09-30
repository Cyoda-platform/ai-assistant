"""
FixCompilationErrorsI1j2PromptConfig Prompt

Generated from config: workflow_configs/agents/prompts/fix_compilation_errors_i1j2/message_0.md
Implements PromptConfig interface with get_name() and get_config() methods.
"""

from .config import get_config
from typing import Any, Dict


class FixCompilationErrorsI1j2PromptConfig:
    """Prompt configuration for fix_compilation_errors_i1j2"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this prompt"""
        return "fix_compilation_errors_i1j2"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> str:
        """Get prompt configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
fix_compilation_errors_i1j2_prompt = FixCompilationErrorsI1j2PromptConfig()
