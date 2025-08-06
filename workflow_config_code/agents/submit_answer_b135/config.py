"""
SubmitAnswerB135AgentConfig Configuration

Generated from config: workflow_configs/agents/submit_answer_b135/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.get_user_info_d8dc.tool import GetUserInfoD8dcToolConfig
from workflow_config_code.tools.web_search_53be.tool import WebSearch53beToolConfig
from workflow_config_code.tools.read_link_3fd1.tool import ReadLink3fd1ToolConfig
from workflow_config_code.tools.web_scrape_9740.tool import WebScrape9740ToolConfig
from workflow_config_code.tools.build_general_application_f281.tool import BuildGeneralApplicationF281ToolConfig
from workflow_config_code.tools.edit_existing_app_design_additional_feature_e0e4.tool import EditExistingAppDesignAdditionalFeatureE0e4ToolConfig
from workflow_config_code.tools.add_new_entity_for_existing_app_0126.tool import AddNewEntityForExistingApp0126ToolConfig
from workflow_config_code.tools.add_new_workflow_7ebe.tool import AddNewWorkflow7ebeToolConfig
from workflow_config_code.tools.edit_api_existing_app_d394.tool import EditApiExistingAppD394ToolConfig
from workflow_config_code.tools.edit_existing_workflow_d34c.tool import EditExistingWorkflowD34cToolConfig
from workflow_config_code.tools.edit_existing_processors_d2d2.tool import EditExistingProcessorsD2d2ToolConfig
from workflow_config_code.tools.init_setup_workflow_d9d0.tool import InitSetupWorkflowD9d0ToolConfig
from workflow_config_code.tools.deploy_cyoda_env_76b1.tool import DeployCyodaEnv76b1ToolConfig
from workflow_config_code.tools.get_cyoda_guidelines_4c97.tool import GetCyodaGuidelines4c97ToolConfig
from workflow_config_code.tools.ui_function_issue_technical_user_7f0f.tool import UiFunctionIssueTechnicalUser7f0fToolConfig
from workflow_config_code.tools.ui_function_list_all_technical_users_2d0b.tool import UiFunctionListAllTechnicalUsers2d0bToolConfig
from workflow_config_code.tools.ui_function_reset_client_secret_1dd6.tool import UiFunctionResetClientSecret1dd6ToolConfig
from workflow_config_code.tools.resume_build_general_application_2af7.tool import ResumeBuildGeneralApplication2af7ToolConfig
from workflow_config_code.tools.get_env_deploy_status_53e7.tool import GetEnvDeployStatus53e7ToolConfig
from workflow_config_code.tools.add_collaborator_to_default_repos_4d46.tool import AddCollaboratorToDefaultRepos4d46ToolConfig
from workflow_config_code.prompts.submit_answer_2821.prompt import SubmitAnswer2821PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "allow_anonymous_users": True,
        "model": {
                "model_name": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 10000
        },
        "tools": [
                {
                        "name": GetUserInfoD8dcToolConfig.get_tool_name()
                },
                {
                        "name": WebSearch53beToolConfig.get_tool_name()
                },
                {
                        "name": ReadLink3fd1ToolConfig.get_tool_name()
                },
                {
                        "name": WebScrape9740ToolConfig.get_tool_name()
                },
                {
                        "name": BuildGeneralApplicationF281ToolConfig.get_tool_name()
                },
                {
                        "name": EditExistingAppDesignAdditionalFeatureE0e4ToolConfig.get_tool_name()
                },
                {
                        "name": AddNewEntityForExistingApp0126ToolConfig.get_tool_name()
                },
                {
                        "name": AddNewWorkflow7ebeToolConfig.get_tool_name()
                },
                {
                        "name": EditApiExistingAppD394ToolConfig.get_tool_name()
                },
                {
                        "name": EditExistingWorkflowD34cToolConfig.get_tool_name()
                },
                {
                        "name": EditExistingProcessorsD2d2ToolConfig.get_tool_name()
                },
                {
                        "name": InitSetupWorkflowD9d0ToolConfig.get_tool_name()
                },
                {
                        "name": DeployCyodaEnv76b1ToolConfig.get_tool_name()
                },
                {
                        "name": GetCyodaGuidelines4c97ToolConfig.get_tool_name()
                },
                {
                        "name": UiFunctionIssueTechnicalUser7f0fToolConfig.get_tool_name()
                },
                {
                        "name": UiFunctionListAllTechnicalUsers2d0bToolConfig.get_tool_name()
                },
                {
                        "name": UiFunctionResetClientSecret1dd6ToolConfig.get_tool_name()
                },
                {
                        "name": ResumeBuildGeneralApplication2af7ToolConfig.get_tool_name()
                },
                {
                        "name": GetEnvDeployStatus53e7ToolConfig.get_tool_name()
                },
                {
                        "name": AddCollaboratorToDefaultRepos4d46ToolConfig.get_tool_name()
                }
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": SubmitAnswer2821PromptConfig.get_name()
                }
        ],
        "tool_choice": "auto",
        "max_iteration": 30,
        "approve": False
}
