"""
PromptSentEf07AgentConfig Configuration

Generated from config: workflow_configs/agents/prompt_sent_ef07/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_collaborator_to_default_repos_865f.tool import AddCollaboratorToDefaultRepos865fToolConfig
from workflow_config_code.tools.get_build_id_from_context_deeb.tool import GetBuildIdFromContextDeebToolConfig
from workflow_config_code.tools.get_user_info_4f38.tool import GetUserInfo4f38ToolConfig
from workflow_config_code.tools.get_env_deploy_status_5dd8.tool import GetEnvDeployStatus5dd8ToolConfig
from workflow_config_code.tools.ui_function_issue_technical_user_808a.tool import UiFunctionIssueTechnicalUser808aToolConfig
from workflow_config_code.prompts.prompt_sent_8926.prompt import PromptSent8926PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "tools": [
                {
                        "name": AddCollaboratorToDefaultRepos865fToolConfig.get_tool_name()
                },
                {
                        "name": GetBuildIdFromContextDeebToolConfig.get_tool_name()
                },
                {
                        "name": GetUserInfo4f38ToolConfig.get_tool_name()
                },
                {
                        "name": GetEnvDeployStatus5dd8ToolConfig.get_tool_name()
                },
                {
                        "name": UiFunctionIssueTechnicalUser808aToolConfig.get_tool_name()
                }
        ],
        "model": {},
        "memory_tags": [
                "chat_deploy_env"
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": PromptSent8926PromptConfig.get_name()
                }
        ],
        "tool_choice": "auto",
        "publish": True
}
