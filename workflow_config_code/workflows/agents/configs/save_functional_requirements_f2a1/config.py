"""
SaveFunctionalRequirementsF2a1AgentConfig Configuration

Generated from config: workflow_configs/agents/configs/save_functional_requirements_f2a1/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.workflows.agents.prompts.save_functional_requirements_f2a1.prompt import SaveFunctionalRequirementsF2a1PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "tools": [
                {
                        "name": AddApplicationResource3d0bToolConfig.get_tool_name()
                }
        ],
        "memory_tags": [
                "save_functional_requirements"
        ],
        "input": {
                "local_fs": [
                        "src/main/java/com/java_template/prototype/functional_requirement.md"
                ]
        },
        "messages": [
                {
                        "role": "user",
                        "content_from_file": SaveFunctionalRequirementsF2a1PromptConfig.get_name()
                }
        ]
}
