"""
ProcessUserInput2e66PromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_2e66/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Please, adjust the functional requirements and the API according to the user request.
- Analyze the user's request and refine functional requirements accordingly.
- Modify the API specification to align with the changes requested by the user while following the Event-Driven Architecture (EDA) principles if applicable.
- Preserve all technical and business logic details.

Rules:
- Once the user is happy with the result or has no further questions, call finish_discussion.
- Be polite, concise, and respond in Markdown.
- If clarification is needed, ask up to 3 short questions or suggestions at a time, and only if absolutely necessary.
- Avoid discussing non-functional requirements.
- Do not ask about frameworks, databases, or infrastructure. Assume Java Spring Boot on Cyoda platform.
- Provide an "Example Ready-to-Copy User Response" in Markdown to make it easy for the user to confirm or adjust.
- Max 10 entities allowed.
Here is the user request:"""
