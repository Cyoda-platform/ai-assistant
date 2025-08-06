"""
GenerateOriginalRequirementsC87eAgentConfig Configuration

Generated from config: workflow_configs/agents/generate_original_requirements_c87e/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.generate_original_requirements_52ef.prompt import \
    GenerateOriginalRequirements52efPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "publish": False,
        "allow_anonymous_users": True,
        "model": {},
        "memory_tags": [
            "requirements_generation",
            "general_memory_tag"
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": GenerateOriginalRequirements52efPromptConfig.get_name()
            }
        ],
        "input": {},
        "output": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/user_requirement.md"
            ]
        }
    }
