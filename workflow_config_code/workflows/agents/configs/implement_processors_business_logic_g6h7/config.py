"""
ImplementProcessorsBusinessLogicG6h7AgentConfig Configuration

Generated from config: workflow_configs/agents/configs/implement_processors_business_logic_g6h7/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.tools.list_directory_files_1ab7.tool import ListDirectoryFiles1ab7ToolConfig
from workflow_config_code.workflows.agents.tools.read_file_2766.tool import ReadFile2766ToolConfig
from workflow_config_code.workflows.agents.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.workflows.agents.prompts.implement_processors_business_logic_g6h7.prompt import ImplementProcessorsBusinessLogicG6h7PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "tools": [
                {
                        "name": ListDirectoryFiles1ab7ToolConfig.get_tool_name()
                },
                {
                        "name": ReadFile2766ToolConfig.get_tool_name()
                },
                {
                        "name": AddApplicationResource3d0bToolConfig.get_tool_name()
                }
        ],
        "memory_tags": [
                "generate_processors_and_criteria"
        ],
        "input": {
                "local_fs": [
                        "src/main/java/com/java_template/prototype/functional_requirement.md",
                        "src/main/resources/functional_requirements/user_requirement.md",
                        "src/main/java/com/java_template/application/processor",
                        "src/main/java/com/java_template/application/criterion"
                ]
        },
        "messages": [
                {
                        "role": "user",
                        "content_from_file": ImplementProcessorsBusinessLogicG6h7PromptConfig.get_name()
                }
        ],
        "tool_choice": "auto",
        "max_iteration": 10,
        "approve": True
}
