"""
Assistant Prompt

Implements PromptConfig interface with get_config() method.
"""

from pathlib import Path
from typing import Dict
from workflow_best_ux.interfaces import PromptConfig
from workflow_best_ux.builders import prompt_config


class AssistantPrompt:
    """Assistant prompt configuration"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this prompt"""
        return "assistant_prompt"

    def __init__(self):
        self.base_path = Path(__file__).parent

    def get_config(self) -> PromptConfig:
        """Get prompt configuration"""
        content = self.read_content()
        return (prompt_config("assistant_prompt")
                .with_content(content)
                .add_variable("platform_name", "Cyoda")
                .add_variable("supported_languages", "Python, Java")
                .build())

    def read_content(self) -> str:
        """Read the markdown content"""
        md_path = self.base_path / "prompt.md"
        if md_path.exists():
            return md_path.read_text(encoding='utf-8')
        return "You are a helpful AI assistant."

    def render_content(self, variables: Dict[str, str] = None) -> str:
        """Render content with variable substitution"""
        content = self.read_content()

        if variables:
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                content = content.replace(placeholder, str(var_value))

        return content


# Create singleton instance
assistant_prompt = AssistantPrompt()

