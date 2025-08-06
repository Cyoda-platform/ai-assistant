"""
ProcessUserInput9a8eAgentConfig Configuration

Generated from config: workflow_configs/agents/process_user_input_9a8e/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.get_user_info_d020.tool import GetUserInfoD020ToolConfig
from workflow_config_code.tools.deploy_cyoda_env_background_01c7.tool import DeployCyodaEnvBackground01c7ToolConfig
from workflow_config_code.tools.finish_discussion_7606.tool import FinishDiscussion7606ToolConfig
from workflow_config_code.prompts.process_user_input_e154.prompt import ProcessUserInputE154PromptConfig


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
                },
                {
                        "name": DeployCyodaEnvBackground01c7ToolConfig.get_tool_name()
                },
                {
                        "name": FinishDiscussion7606ToolConfig.get_tool_name()
                }
        ],
        "memory_tags": [
                "chat_deploy_env"
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": ProcessUserInputE154PromptConfig.get_name()
                }
        ],
        "tool_choice": "auto",
        "max_iteration": 30
}
