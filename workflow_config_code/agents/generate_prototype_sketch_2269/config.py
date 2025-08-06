"""
GeneratePrototypeSketch2269AgentConfig Configuration

Generated from config: workflow_configs/agents/generate_prototype_sketch_2269/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_collaborator_to_default_repos_ffe7.tool import \
    AddCollaboratorToDefaultReposFfe7ToolConfig
from workflow_config_code.tools.list_directory_files_1ab7.tool import ListDirectoryFiles1ab7ToolConfig
from workflow_config_code.tools.read_file_2766.tool import ReadFile2766ToolConfig
from workflow_config_code.prompts.generate_prototype_sketch_4b85.prompt import GeneratePrototypeSketch4b85PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "allow_anonymous_users": True,
        "model": {},
        "tools": [
            {
                "name": AddCollaboratorToDefaultReposFfe7ToolConfig.get_tool_name()
            },
            {
                "name": ListDirectoryFiles1ab7ToolConfig.get_tool_name()
            },
            {
                "name": ReadFile2766ToolConfig.get_tool_name()
            }
        ],
        "tool_choice": "auto",
        "max_iteration": 30,
        "memory_tags": [
            "configs_generation",
            "prototype_generation"
        ],
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/functional_requirement.md",
                "src/main/java/com/java_template/prototype/user_requirement.md"
            ]
        },
        "output": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/EntityControllerPrototype.java"
            ]
        },
        "messages": [
            {
                "role": "user",
                "content_from_file": GeneratePrototypeSketch4b85PromptConfig.get_name()
            }
        ]
    }
