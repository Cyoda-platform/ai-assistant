"""
PromptSentA239PyAgentConfig Configuration

Generated from config: workflow_configs/agents/configs/prompt_sent_a239_py/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.prompts.prompt_sent_f4c8_py.prompt import PromptSentF4c8PyPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "approve": True,
        "model": {
                "model_name": "gpt-5-mini"
        },
        "messages": [
                {
                        "role": "user",
                        "content_from_file": PromptSentF4c8PyPromptConfig.get_name()
                }
        ],
        "publish": True
}
