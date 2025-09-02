"""
GenerateEntitiesRequirementsAcccAgentConfig Configuration

Generated from config: workflow_configs/agents/generate_entities_requirements_accc/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.generate_entities_requirements_1641.prompt import \
    GenerateEntitiesRequirements1641PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "publish": False,
        "allow_anonymous_users": True,
        "model": {},
        "memory_tags": [
            "GenerateEntitiesRequirements1641PromptConfig",
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": GenerateEntitiesRequirements1641PromptConfig.get_name()
            }
        ],
        "input": {
            "local_fs": [
                "src/main/resources/functional_requirements/entities.md"
            ]
        },
        "output": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/entities_requirement.json"
            ]
        },
        "response_format": {
            "name": "arbitrary_list_wrapper",
            "description": "Top-level object wrapping an arbitrary JSON array",
            "schema": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {}
                    }
                },
                "required": ["entities"],
                "additionalProperties": False
            }
        }
    }
