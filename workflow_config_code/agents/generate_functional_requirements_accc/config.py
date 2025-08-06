"""
GenerateFunctionalRequirementsAcccAgentConfig Configuration

Generated from config: workflow_configs/agents/generate_functional_requirements_accc/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.generate_functional_requirements_1641.prompt import \
    GenerateFunctionalRequirements1641PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "publish": False,
        "allow_anonymous_users": True,
        "model": {},
        "memory_tags": [
            "requirements_generation",
            "configs_generation"
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": GenerateFunctionalRequirements1641PromptConfig.get_name()
            }
        ],
        "input": {},
        "output": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/functional_requirement.md"
            ]
        }
    }
