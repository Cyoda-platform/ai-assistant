"""
ProcessUserInput57d2AgentConfig Configuration

Generated from config: workflow_configs/agents/process_user_input_57d2/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable

from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.tools.add_collaborator_to_default_repos_865f.tool import \
    AddCollaboratorToDefaultRepos865fToolConfig
from workflow_config_code.tools.get_user_info_4f38.tool import GetUserInfo4f38ToolConfig
from workflow_config_code.tools.get_cyoda_guidelines_f3bb.tool import GetCyodaGuidelinesF3bbToolConfig
from workflow_config_code.tools.finish_discussion_8f05.tool import FinishDiscussion8f05ToolConfig
from workflow_config_code.tools.get_env_deploy_status_5dd8.tool import GetEnvDeployStatus5dd8ToolConfig
from workflow_config_code.tools.list_directory_files_1ab7.tool import ListDirectoryFiles1ab7ToolConfig
from workflow_config_code.tools.read_file_2766.tool import ReadFile2766ToolConfig
from workflow_config_code.tools.ui_function_issue_technical_user_808a.tool import \
    UiFunctionIssueTechnicalUser808aToolConfig
from workflow_config_code.tools.ui_function_list_all_technical_users_7489.tool import \
    UiFunctionListAllTechnicalUsers7489ToolConfig
from workflow_config_code.tools.ui_function_reset_client_secret_1cf5.tool import \
    UiFunctionResetClientSecret1cf5ToolConfig
from workflow_config_code.prompts.process_user_input_33bb.prompt import ProcessUserInput33bbPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "allow_anonymous_users": True,
        "model": {},
        "tools": [
            {
                "name": AddCollaboratorToDefaultRepos865fToolConfig.get_tool_name()
            },
            {
                "name": GetUserInfo4f38ToolConfig.get_tool_name()
            },
            {
                "name": GetCyodaGuidelinesF3bbToolConfig.get_tool_name()
            },
            {
                "name": FinishDiscussion8f05ToolConfig.get_tool_name()
            },
            {
                "name": GetEnvDeployStatus5dd8ToolConfig.get_tool_name()
            },
            {
                "name": UiFunctionIssueTechnicalUser808aToolConfig.get_tool_name()
            },
            {
                "name": UiFunctionListAllTechnicalUsers7489ToolConfig.get_tool_name()
            },
            {
                "name": UiFunctionResetClientSecret1cf5ToolConfig.get_tool_name()
            },
            {
                "name": AddApplicationResource3d0bToolConfig.get_tool_name()
            },
            {
                "name": ListDirectoryFiles1ab7ToolConfig.get_tool_name()
            },
            {
                "name": ReadFile2766ToolConfig.get_tool_name()
            }
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": ProcessUserInput33bbPromptConfig.get_name()
            }
        ],
        "tool_choice": "auto",
        "max_iteration": 30,
        "approve": True
    }
