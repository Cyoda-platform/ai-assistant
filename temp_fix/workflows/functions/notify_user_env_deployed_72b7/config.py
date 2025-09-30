"""
NotifyUserEnvDeployed72b7PromptConfig Configuration

Generated from config: workflow_configs/prompts/notify_user_env_deployed_72b7/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Call `get_user_info` to get user environment URL and its status (deployed/not deployed).`
 If the environment is deployed: tell the user that their environment (tell the env url) is deployed and there is no need to deploy it again. So you proceed to building the application.
 If the environment is not deployed: tell the user that you've scheduled the deployment and it will be available soon at {env url}. You will proceed to building the application in parallel."""
