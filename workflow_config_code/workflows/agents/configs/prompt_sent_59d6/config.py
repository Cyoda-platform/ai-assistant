"""
PromptSent59d6AgentConfig Configuration

Generated from config: workflow_configs/agents/configs/prompt_sent_59d6/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.prompts.prompt_sent_88b3.prompt import PromptSent88b3PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "approve": True,
        "model": {
                "model_name": "gpt-4o-mini"
        },
        "messages": [
                {
                        "role": "user",
                        "content_from_file": PromptSent88b3PromptConfig.get_name()
                }
        ],
        "publish": True
}
