"""
ProcessUserInputE154PromptConfig Configuration

Generated from config: workflow_configs/prompts/process_user_input_e154/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Step 1: Call `get_user_info` to check if the user is logged in.
• If the user is not logged in, respond: '😊 Please log in to your account so that we could start deploying your environment.
If you don't have an account yet, no worries — a new account will be added for you automatically.

🔐 Logging in is necessary so we can create and link your personal Cyoda environment to your account.

✅ Once you're logged in, just drop a message here and I'll get everything set up for you!' Do not proceed further until the user confirms they're logged in.

Step 2: Once the user is confirmed to be logged in, call `get_user_info` again to check if their Cyoda environment is already deployed.

• If the environment is already deployed, Inform the user: 'Great! Your Cyoda environment (environment name) is already active and ready to use. Let's proceed with setting up your application and call `finish_discussion` immediately to proceed to the next step.

• If the environment is not deployed, call `deploy_cyoda_env` and immediately call `finish_discussion`.
• Inform the user: 'I'm now deploying your Cyoda environment. Your build ID is {{build_id}}. You can check the deployment status in a new chat while this one stays focused on setting up your Cyoda application.'

IMPORTANT:
If the user is not logged in - you can tell them that they can proceed without logging in, but then they will have to deploy the environment in a separate chat once they are logged in.
To proceed without logging in they need to explicitly confirm that they want to proceed without logging in. Then call `deploy_cyoda_env` and immediately call `finish_discussion`.
"""