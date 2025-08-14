"""
ProcessUserInput2185AgentConfig Configuration

Generated from config: workflow_configs/agents/process_user_input_2185/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable

from workflow_config_code.prompts.process_prototype_discussion_0000.prompt import \
    ProcessPrototypeDiscussion0000PromptConfig
from workflow_config_code.tools.add_collaborator_to_default_repos_ffe7.tool import AddCollaboratorToDefaultReposFfe7ToolConfig
from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.tools.get_cyoda_guidelines_c748.tool import GetCyodaGuidelinesC748ToolConfig
from workflow_config_code.tools.list_directory_files_1ab7.tool import ListDirectoryFiles1ab7ToolConfig
from workflow_config_code.tools.web_search_7e4b.tool import WebSearch7e4bToolConfig
from workflow_config_code.tools.read_link_c472.tool import ReadLinkC472ToolConfig
from workflow_config_code.tools.web_scrape_bc54.tool import WebScrapeBc54ToolConfig
from workflow_config_code.tools.read_file_2766.tool import ReadFile2766ToolConfig
from workflow_config_code.tools.finish_discussion_3dd8.tool import FinishDiscussion3dd8ToolConfig
from workflow_config_code.prompts.process_user_input_4c0e.prompt import ProcessUserInput4c0ePromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "approve": True,
        "allow_anonymous_users": True,
        "model": {},
        "memory_tags": [
            "prototype_generation"
        ],
        "tools": [
            {
                "name": AddApplicationResource3d0bToolConfig.get_tool_name()
            },
            {
                "name": ListDirectoryFiles1ab7ToolConfig.get_tool_name()
            },
            {
                "name": ReadFile2766ToolConfig.get_tool_name()
            },
            {
                "name": GetCyodaGuidelinesC748ToolConfig.get_tool_name()
            },
            {
                "name": FinishDiscussion3dd8ToolConfig.get_tool_name()
            },
            {
                "name": AddCollaboratorToDefaultReposFfe7ToolConfig.get_tool_name()
            }
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": ProcessPrototypeDiscussion0000PromptConfig.get_name()
            }
        ],
        "tool_choice": "auto",
        "max_iteration": 30
}
