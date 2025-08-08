"""
ParseWorkflowConfigsB3c2AgentConfig Configuration

Configuration data for the parse workflow configs agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.prompts.parse_workflow_configs_b3c2.prompt import ParseWorkflowConfigsB3c2PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "tools": [
            {
                "name": AddApplicationResource3d0bToolConfig.get_tool_name()
            }
        ],
        "memory_tags": [
            "parse_workflow_configs"
        ],
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/functional_requirement.md"
            ]
        },
        "messages": [
            {
                "role": "user",
                "content_from_file": ParseWorkflowConfigsB3c2PromptConfig.get_name()
            }
        ]
    }
