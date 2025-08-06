"""
NotifyUserEnvDeployed58e2AgentConfig Configuration

Generated from config: workflow_configs/agents/notify_user_env_deployed_58e2/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.get_user_info_d020.tool import GetUserInfoD020ToolConfig
from workflow_config_code.prompts.notify_user_env_deployed_72b7.prompt import NotifyUserEnvDeployed72b7PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "allow_anonymous_users": True,
        "model": {},
        "tools": [
                {
                        "name": GetUserInfoD020ToolConfig.get_tool_name()
                }
        ],
        "memory_tags": [
                "chat_deploy_env"
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": NotifyUserEnvDeployed72b7PromptConfig.get_name()
                }
        ],
        "tool_choice": "auto",
        "max_iteration": 30
}
