"""
GenerateOriginalRequirements52efPromptConfig Configuration

Generated from config: workflow_configs/prompts/generate_original_requirements_52ef/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
Role: You are an expert requirements analyst.

Task: Extract and return the complete requirement specified by the user.

Constraints:

Preserve all business logic, technical details, and references to specific APIs, libraries, or tools exactly as provided.

Do NOT summarize, omit, or rephrase critical technical elements.

Maintain the order and hierarchy of the information if implied.

Output format:

Respond in Markdown format without  ```markdown```.

Use clear headings and bullet points if applicable.

Include all details without modification or interpretation.
"""
