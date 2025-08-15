"""
GenerateControllerD4e3AgentConfig Configuration

Configuration data for the generate controller agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.tools.list_directory_files_1161.tool import ListDirectoryFiles1161ToolConfig
from workflow_config_code.tools.list_directory_files_1ab7.tool import ListDirectoryFiles1ab7ToolConfig
from workflow_config_code.tools.read_file_2766.tool import ReadFile2766ToolConfig
from workflow_config_code.prompts.generate_controller_d4e3.prompt import GenerateControllerD4e3PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "tools": [
            {"name": ListDirectoryFiles1ab7ToolConfig.get_tool_name()},
            {"name": ReadFile2766ToolConfig.get_tool_name()},
            {"name": AddApplicationResource3d0bToolConfig.get_tool_name()}
        ],
        "memory_tags": [
            "generate_controller"
        ],
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/functional_requirement.md"
            ]
        },
        "messages": [
            {
                "role": "user",
                "content_from_file": GenerateControllerD4e3PromptConfig.get_name()
            }
        ]
    }
