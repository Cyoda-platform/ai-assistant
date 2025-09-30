"""
ProcessUserInputDd02PyAgentConfig Configuration

Generated from config: workflow_configs/agents/configs/process_user_input_dd02_py/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.tools.add_collaborator_to_default_repos_865f.tool import AddCollaboratorToDefaultRepos865fToolConfig
from workflow_config_code.workflows.agents.tools.get_cyoda_guidelines_f3bb.tool import GetCyodaGuidelinesF3bbToolConfig
from workflow_config_code.workflows.agents.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.workflows.agents.tools.list_directory_files_1ab7.tool import ListDirectoryFiles1ab7ToolConfig
from workflow_config_code.workflows.agents.tools.read_file_2766.tool import ReadFile2766ToolConfig
from workflow_config_code.workflows.agents.tools.finish_discussion_69bc.tool import FinishDiscussion69bcToolConfig
from workflow_config_code.workflows.agents.prompts.process_user_input_610e_py.prompt import ProcessUserInput610ePyPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "allow_anonymous_users": True,
        "model": {
                "model_name": "gpt-4o-mini"
        },
        "tools": [
                {
                        "name": AddCollaboratorToDefaultRepos865fToolConfig.get_tool_name()
                },
                {
                        "name": GetCyodaGuidelinesF3bbToolConfig.get_tool_name()
                },
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
                        "name": FinishDiscussion69bcToolConfig.get_tool_name()
                }
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": ProcessUserInput610ePyPromptConfig.get_name()
                }
        ],
        "tool_choice": "auto",
        "max_iteration": 30,
        "approve": True
}
