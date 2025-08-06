"""
ExtractEntitiesFromPrototype22c6AgentConfig Configuration

Generated from config: workflow_configs/agents/extract_entities_from_prototype_22c6/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_collaborator_to_default_repos_ffe7.tool import \
    AddCollaboratorToDefaultReposFfe7ToolConfig
from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.prompts.extract_entities_from_prototype_e7fa.prompt import \
    ExtractEntitiesFromPrototypeE7faPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "tools": [
            {
                "name": AddCollaboratorToDefaultReposFfe7ToolConfig.get_tool_name()
            },
            {
                "name": AddApplicationResource3d0bToolConfig.get_tool_name()
            }
        ],
        "memory_tags": [
            "configs_generation"
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": ExtractEntitiesFromPrototypeE7faPromptConfig.get_name()
            }
        ],
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/functional_requirement.md"
            ]
        },
        "tool_choice": "auto",
        "max_iteration": 5,
        "approve": True
    }
