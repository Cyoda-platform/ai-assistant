"""
EditAppPythonAgentConfig Configuration

Agent configuration for editing existing Python applications.
"""

from typing import Any, Dict, Callable

from workflow_config_code.workflows.agents.prompts.edit_app_python.prompt import EditAppPythonPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "agent_type": "auggie",
        "script_path": "workflow/scripts/auggie_example.sh",
        "prompt": EditAppPythonPromptConfig.get_config(),
        "model": "haiku4.5"
}
