"""
EnhanceProcessorsG6h7AgentConfig Configuration

Configuration data for the enhance processors agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.enhance_processors_g6h7.prompt import EnhanceProcessorsG6h7PromptConfig
from workflow_config_code.tools.validate_workflow_processors.tool import ValidateWorkflowProcessorsToolConfig

from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {
        },
        "tools": [
            {
                "name": AddApplicationResource3d0bToolConfig.get_tool_name()
            },
            {
                "name": ValidateWorkflowProcessorsToolConfig.get_tool_name()
            }
        ],
        "memory_tags": [
             "generate_processors_and_criteria"
        ],
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/application/processor",
                "src/main/java/com/java_template/application/entity",
                "src/main/java/com/java_template/prototype/functional_requirement.md",
                "src/main/java/com/java_template/prototype/user_requirement.md"
            ]
        },
        "messages": [
            {
                "role": "user",
                "content_from_file": EnhanceProcessorsG6h7PromptConfig.get_name()
            }
        ],
        "tool_choice": "auto",
        "max_iteration": 10,
        "approve": True
    }
