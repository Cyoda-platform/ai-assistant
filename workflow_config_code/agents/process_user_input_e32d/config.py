"""
ProcessUserInputE32dAgentConfig Configuration

Generated from config: workflow_configs/agents/process_user_input_e32d/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_collaborator_to_default_repos_865f.tool import AddCollaboratorToDefaultRepos865fToolConfig
from workflow_config_code.tools.get_user_info_4f38.tool import GetUserInfo4f38ToolConfig
from workflow_config_code.tools.read_link_16a6.tool import ReadLink16a6ToolConfig
from workflow_config_code.tools.add_new_entity_for_existing_app_cb15.tool import AddNewEntityForExistingAppCb15ToolConfig
from workflow_config_code.tools.add_new_workflow_f610.tool import AddNewWorkflowF610ToolConfig
from workflow_config_code.tools.edit_api_existing_app_21f5.tool import EditApiExistingApp21f5ToolConfig
from workflow_config_code.tools.edit_existing_workflow_f38d.tool import EditExistingWorkflowF38dToolConfig
from workflow_config_code.tools.edit_existing_processors_b3f3.tool import EditExistingProcessorsB3f3ToolConfig
from workflow_config_code.tools.get_cyoda_guidelines_f3bb.tool import GetCyodaGuidelinesF3bbToolConfig
from workflow_config_code.tools.finish_discussion_782e.tool import FinishDiscussion782eToolConfig
from workflow_config_code.tools.get_env_deploy_status_5dd8.tool import GetEnvDeployStatus5dd8ToolConfig
from workflow_config_code.tools.ui_function_issue_technical_user_808a.tool import UiFunctionIssueTechnicalUser808aToolConfig
from workflow_config_code.tools.ui_function_list_all_technical_users_7489.tool import UiFunctionListAllTechnicalUsers7489ToolConfig
from workflow_config_code.tools.ui_function_reset_client_secret_1cf5.tool import UiFunctionResetClientSecret1cf5ToolConfig
from workflow_config_code.prompts.process_user_input_a094.prompt import ProcessUserInputA094PromptConfig


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
                        "name": ReadLink16a6ToolConfig.get_tool_name()
                },
                {
                        "name": AddNewEntityForExistingAppCb15ToolConfig.get_tool_name()
                },
                {
                        "name": AddNewWorkflowF610ToolConfig.get_tool_name()
                },
                {
                        "name": EditApiExistingApp21f5ToolConfig.get_tool_name()
                },
                {
                        "name": EditExistingWorkflowF38dToolConfig.get_tool_name()
                },
                {
                        "name": EditExistingProcessorsB3f3ToolConfig.get_tool_name()
                },
                {
                        "name": GetCyodaGuidelinesF3bbToolConfig.get_tool_name()
                },
                {
                        "name": FinishDiscussion782eToolConfig.get_tool_name()
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
                }
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": ProcessUserInputA094PromptConfig.get_name()
                }
        ],
        "tool_choice": "auto",
        "max_iteration": 30,
        "approve": True
}
