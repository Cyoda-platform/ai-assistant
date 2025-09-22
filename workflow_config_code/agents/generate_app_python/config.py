"""
GenerateProcessorsAndCriteriaE5f4AgentConfig Configuration

Configuration data for the generate processors and criteria agent.
"""

from typing import Any, Dict, Callable

from workflow_config_code.prompts.generate_app_python.prompt import GenerateAppPythonPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "agent_type": "auggie",
        "script_path": "workflow/scripts/auggie_example.sh",
        "prompt": GenerateAppPythonPromptConfig.get_config(),
        "model": "sonnet4"
    }
