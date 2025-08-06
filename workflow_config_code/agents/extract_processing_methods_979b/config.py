"""
ExtractProcessingMethods979bAgentConfig Configuration

Generated from config: workflow_configs/agents/extract_processing_methods_979b/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_collaborator_to_default_repos_ffe7.tool import \
    AddCollaboratorToDefaultReposFfe7ToolConfig
from workflow_config_code.tools.add_application_resource_56b5.tool import AddApplicationResource56b5ToolConfig
from workflow_config_code.tools.list_directory_files_6ec5.tool import ListDirectoryFiles6ec5ToolConfig
from workflow_config_code.prompts.extract_processing_methods_b08b.prompt import ExtractProcessingMethodsB08bPromptConfig


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
                "name": AddApplicationResource56b5ToolConfig.get_tool_name()
            },
            {
                "name": ListDirectoryFiles6ec5ToolConfig.get_tool_name()
            }
        ],
        "memory_tags": [
            "processing_methods_extraction"
        ],
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
        "messages": [
            {
                "role": "user",
                "content_from_file": ExtractProcessingMethodsB08bPromptConfig.get_name()
            }
        ],
        "tool_choice": "auto",
        "max_iteration": 10,
        "approve": True
    }
