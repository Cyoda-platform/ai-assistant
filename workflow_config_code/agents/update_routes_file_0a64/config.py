"""
UpdateRoutesFile0a64AgentConfig Configuration

Generated from config: workflow_configs/agents/update_routes_file_0a64/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_collaborator_to_default_repos_ffe7.tool import \
    AddCollaboratorToDefaultReposFfe7ToolConfig
from workflow_config_code.tools.get_file_contents_278c.tool import GetFileContents278cToolConfig
from workflow_config_code.tools.list_directory_files_1f6c.tool import ListDirectoryFiles1f6cToolConfig
from workflow_config_code.tools.get_entity_pojo_contents_04a3.tool import GetEntityPojoContents04a3ToolConfig
from workflow_config_code.prompts.update_routes_file_cb25.prompt import UpdateRoutesFileCb25PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "memory_tags": [
            "controller_validation"
        ],
        "tools": [
            {
                "name": AddCollaboratorToDefaultReposFfe7ToolConfig.get_tool_name()
            },
            {
                "name": GetFileContents278cToolConfig.get_tool_name()
            },
            {
                "name": ListDirectoryFiles1f6cToolConfig.get_tool_name()
            },
            {
                "name": GetEntityPojoContents04a3ToolConfig.get_tool_name()
            }
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": UpdateRoutesFileCb25PromptConfig.get_name()
            }
        ],
        "tool_choice": "auto",
        "max_iteration": 10,
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/application/controller/Controller.java"
            ]
        },
        "output": {
            "local_fs": [
                "src/main/java/com/java_template/application/controller/Controller.java"
            ]
        },
        "approve": True
    }
