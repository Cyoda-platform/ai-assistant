"""
GenerateFunctionalRequirements1641PromptConfig Configuration

Generated from config: workflow_configs/prompts/generate_functional_requirements_1641/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: \
        """Please return a well-formatted final version of the functional requirements confirmed by the user.
- The response must be in Markdown format.
- Preserve all business logic, technical details, entity definitions, events, and API specifications exactly as confirmed by the user.
- Do not add new assumptions or modifications.
- This should represent the finalized version, suitable for direct use in documentation or implementation.
"""
