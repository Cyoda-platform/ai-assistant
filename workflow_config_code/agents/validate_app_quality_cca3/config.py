"""
ValidateAppQualityCca3AgentConfig Configuration

Generated from config: workflow_configs/agents/validate_app_quality_cca3/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_collaborator_to_default_repos_ffe7.tool import AddCollaboratorToDefaultReposFfe7ToolConfig
from workflow_config_code.tools.get_file_contents_2480.tool import GetFileContents2480ToolConfig
from workflow_config_code.tools.list_directory_files_1161.tool import ListDirectoryFiles1161ToolConfig
from workflow_config_code.prompts.validate_app_quality_1b5c.prompt import ValidateAppQuality1b5cPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "model": {},
        "memory_tags": [
                "entity_processing_logic_validation"
        ],
        "tools": [
                {
                        "name": AddCollaboratorToDefaultReposFfe7ToolConfig.get_tool_name()
                },
                {
                        "name": GetFileContents2480ToolConfig.get_tool_name()
                },
                {
                        "name": ListDirectoryFiles1161ToolConfig.get_tool_name()
                }
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": ValidateAppQuality1b5cPromptConfig.get_name()
                }
        ],
        "tool_choice": "auto",
        "max_iteration": 15,
        "approve": False
}
