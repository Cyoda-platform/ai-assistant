"""
DefineFunctionalRequirements8ee2AgentConfig Configuration

Generated from config: workflow_configs/agents/define_functional_requirements_8ee2/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.define_functional_requirements_67a6.prompt import \
    DefineFunctionalRequirements67a6PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "name": "define_functional_requirements_8ee2",
        "type": "prompt",
        "publish": True,
        "allow_anonymous_users": True,
        "model": {},
        "memory_tags": [
            "process_initial_requirement",
            "requirements_generation"
        ],
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/user_requirement.md"
            ]
        },
        "messages": [
            {
                "role": "user",
                "content_from_file": DefineFunctionalRequirements67a6PromptConfig.get_name()
            }
        ]
    }
