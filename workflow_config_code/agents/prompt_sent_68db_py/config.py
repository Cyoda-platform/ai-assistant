"""
PromptSent68dbAgentConfig Configuration

Generated from config: workflow_configs/agents/prompt_sent_68db/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.prompt_sent_d866.prompt import PromptSentD866PromptConfig
from workflow_config_code.prompts.prompt_sent_d866_py.prompt import PromptSentD866PyPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "approve": True,
        "model": {"model_name": "gpt-4o-mini"},
        "messages": [
                {
                        "role": "user",
                        "content_from_file": PromptSentD866PyPromptConfig.get_name()
                }
        ],
        "publish": True
}
