"""
DefineFunctionalRequirements8ee2AgentConfig Configuration

Generated from config: workflow_configs/agents/define_functional_requirements_8ee2/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.define_functional_requirements_67a6.prompt import \
    DefineFunctionalRequirements67a6PromptConfig
from workflow_config_code.prompts.define_functional_requirements_67a6_py.prompt import \
    DefineFunctionalRequirements67a6PyPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "agent_type": "auggie",
        "script_path": "workflow/scripts/auggie_example.sh",
        "prompt": DefineFunctionalRequirements67a6PyPromptConfig.get_config(),
        "model": "sonnet4",
        "input": {
            "local_fs": [
                "functional_requirements/user_requirement.md"
            ]
        }
    }
