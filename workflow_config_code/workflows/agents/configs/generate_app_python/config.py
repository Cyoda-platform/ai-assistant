"""
GenerateAppPythonAgentConfig Configuration

Generated from config: workflow_configs/agents/configs/generate_app_python/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable

from workflow_config_code.workflows.agents.prompts.generate_app_python.prompt import GenerateAppPythonPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "agent_type": "auggie",
        "script_path": "workflow/scripts/auggie_example.sh",
        "prompt": GenerateAppPythonPromptConfig.get_config(),
        "model": "haiku4.5"
}
