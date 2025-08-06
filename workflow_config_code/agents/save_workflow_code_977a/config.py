"""
SaveWorkflowCode977aAgentConfig Configuration

Generated from config: workflow_configs/agents/save_workflow_code_977a/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.save_workflow_code_959f.prompt import SaveWorkflowCode959fPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "publish": False,
        "model": {},
        "output": {},
        "memory_tags": [
                "workflow_generation"
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": SaveWorkflowCode959fPromptConfig.get_name()
                }
        ],
        "input": {
                "local_fs": [
                        "src/main/java/com/java_template/application/workflow_prototypes/{EntityName}.txt",
                        "src/main/java/com/java_template/prototype/functional_requirement.md"
                ]
        }
}
