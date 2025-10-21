"""
EditAppJavaAgentConfig Configuration

Agent configuration for editing existing Java applications.
"""

from typing import Any, Dict, Callable

from workflow_config_code.workflows.agents.prompts.edit_app_java.prompt import EditAppJavaPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "agent_type": "auggie",
        "script_path": "workflow/scripts/auggie_example.sh",
        "prompt": EditAppJavaPromptConfig.get_config(),
        "model": "sonnet4"
}
