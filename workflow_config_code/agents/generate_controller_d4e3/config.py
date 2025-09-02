"""
GenerateControllerD4e3AgentConfig Configuration

Configuration data for the generate controller agent using Auggie CLI.
"""

from typing import Any, Dict, Callable

from workflow_config_code.prompts.generate_processors_and_criteria_e5f4.prompt import \
    GenerateProcessorsAndCriteriaE5f4PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "agent_type": "auggie",
        "script_path": "workflow/scripts/auggie_example.sh",
        "prompt": GenerateProcessorsAndCriteriaE5f4PromptConfig.get_config(),
        "model": "sonnet4"
    }
