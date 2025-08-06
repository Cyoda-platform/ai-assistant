"""
DesignWorkflowConfigFromCodeFe21AgentConfig Configuration

Generated from config: workflow_configs/agents/design_workflow_config_from_code_fe21/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.design_workflow_config_from_code_a364.prompt import DesignWorkflowConfigFromCodeA364PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "publish": False,
        "model": {},
        "memory_tags": [
                "workflow_generation"
        ],
        "output": {
                "local_fs": [
                        "src/main/java/com/java_template/application/workflow/{EntityName}.json"
                ]
        },
        "messages": [
                {
                        "role": "user",
                        "content_from_file": DesignWorkflowConfigFromCodeA364PromptConfig.get_name()
                }
        ]
}
