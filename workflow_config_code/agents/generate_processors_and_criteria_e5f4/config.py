"""
GenerateProcessorsAndCriteriaE5f4AgentConfig Configuration

Configuration data for the generate processors and criteria agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.prompts.generate_processors_and_criteria_e5f4.prompt import GenerateProcessorsAndCriteriaE5f4PromptConfig


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
            "generate_processors_and_criteria"
        ],
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/functional_requirement.md",
                "src/main/java/com/java_template/prototype/user_requirement.md",
                "src/main/java/com/java_template/application/workflow-prototypes"
            ]
        },
        "messages": [
            {
                "role": "user",
                "content_from_file": GenerateProcessorsAndCriteriaE5f4PromptConfig.get_name()
            }
        ]
    }
