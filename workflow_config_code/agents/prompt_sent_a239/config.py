"""
PromptSentA239AgentConfig Configuration

Generated from config: workflow_configs/agents/prompt_sent_a239/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.prompt_sent_f4c8.prompt import PromptSentF4c8PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "approve": True,
        "model": {},
        "messages": [
                {
                        "role": "user",
                        "content_from_file": PromptSentF4c8PromptConfig.get_name()
                }
        ],
        "publish": True
}
