"""
GenerateWorkflowFromRequirements0000AgentConfig Configuration

Generated from config: workflow_configs/agents/generate_workflow_from_requirements_0000/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.tools.list_directory_files_1ab7.tool import ListDirectoryFiles1ab7ToolConfig
from workflow_config_code.prompts.generate_workflow_from_requirements_0000.prompt import \
    GenerateWorkflowFromRequirements0000PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "name": "generate_workflow_from_requirements_0000",
        "model": {},
        "memory_tags": [
            "configs_generation"
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": GenerateWorkflowFromRequirements0000PromptConfig.get_name()
            }
        ],
        "tools": [
            {
                "name": AddApplicationResource3d0bToolConfig.get_tool_name()
            },
            {
                "name": ListDirectoryFiles1ab7ToolConfig.get_tool_name()
            }
        ],
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/functional_requirement.md"
            ]
        },
        "publish": False
    }
