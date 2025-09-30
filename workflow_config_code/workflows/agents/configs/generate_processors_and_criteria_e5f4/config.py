"""
GenerateProcessorsAndCriteriaE5f4AgentConfig Configuration

Generated from config: workflow_configs/agents/configs/generate_processors_and_criteria_e5f4/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.workflows.agents.tools.validate_workflow_processors.tool import ValidateWorkflowProcessorsToolConfig
from workflow_config_code.workflows.agents.tools.extract_workflow_components_k2l3.tool import ExtractWorkflowComponentsK2l3ToolConfig
from workflow_config_code.workflows.agents.prompts.generate_processors_and_criteria_e5f4.prompt import GenerateProcessorsAndCriteriaE5f4PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "tools": [
                {
                        "name": AddApplicationResource3d0bToolConfig.get_tool_name()
                },
                {
                        "name": ValidateWorkflowProcessorsToolConfig.get_tool_name()
                },
                {
                        "name": ExtractWorkflowComponentsK2l3ToolConfig.get_tool_name()
                }
        ],
        "memory_tags": [
                "generate_processors_and_criteria"
        ],
        "input": {
                "local_fs": [
                        "src/main/java/com/java_template/prototype/functional_requirement.md",
                        "src/main/resources/functional_requirements/user_requirement.md",
                        "src/main/resources/workflow"
                ]
        },
        "messages": [
                {
                        "role": "user",
                        "content_from_file": GenerateProcessorsAndCriteriaE5f4PromptConfig.get_name()
                }
        ]
}
