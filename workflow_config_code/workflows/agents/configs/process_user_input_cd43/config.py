"""
ProcessUserInputCd43AgentConfig Configuration

Generated from config: workflow_configs/agents/configs/process_user_input_cd43/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.tools.add_collaborator_to_default_repos_ffe7.tool import AddCollaboratorToDefaultReposFfe7ToolConfig
from workflow_config_code.workflows.agents.tools.get_cyoda_guidelines_c748.tool import GetCyodaGuidelinesC748ToolConfig
from workflow_config_code.workflows.agents.tools.web_search_7e4b.tool import WebSearch7e4bToolConfig
from workflow_config_code.workflows.agents.tools.read_link_c472.tool import ReadLinkC472ToolConfig
from workflow_config_code.workflows.agents.tools.web_scrape_bc54.tool import WebScrapeBc54ToolConfig
from workflow_config_code.workflows.agents.tools.finish_discussion_7c9e.tool import FinishDiscussion7c9eToolConfig
from workflow_config_code.workflows.agents.tools.list_directory_files_1ab7.tool import ListDirectoryFiles1ab7ToolConfig
from workflow_config_code.workflows.agents.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.workflows.agents.tools.read_file_2766.tool import ReadFile2766ToolConfig
from workflow_config_code.workflows.agents.prompts.process_user_input_2e66.prompt import ProcessUserInput2e66PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "allow_anonymous_users": True,
        "model": {},
        "memory_tags": [
                "requirements_generation"
        ],
        "tools": [
                {
                        "name": AddCollaboratorToDefaultReposFfe7ToolConfig.get_tool_name()
                },
                {
                        "name": GetCyodaGuidelinesC748ToolConfig.get_tool_name()
                },
                {
                        "name": WebSearch7e4bToolConfig.get_tool_name()
                },
                {
                        "name": ReadLinkC472ToolConfig.get_tool_name()
                },
                {
                        "name": WebScrapeBc54ToolConfig.get_tool_name()
                },
                {
                        "name": FinishDiscussion7c9eToolConfig.get_tool_name()
                },
                {
                        "name": ListDirectoryFiles1ab7ToolConfig.get_tool_name()
                },
                {
                        "name": AddApplicationResource3d0bToolConfig.get_tool_name()
                },
                {
                        "name": ReadFile2766ToolConfig.get_tool_name()
                }
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": ProcessUserInput2e66PromptConfig.get_name()
                }
        ],
        "tool_choice": "auto",
        "max_iteration": 30,
        "approve": True
}
