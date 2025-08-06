"""
GenerateCriteriaFromWorkflows42a6AgentConfig Configuration

Generated from config: workflow_configs/agents/generate_criteria_from_workflows_42a6/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_application_resource_3968.tool import AddApplicationResource3968ToolConfig
from workflow_config_code.prompts.generate_criteria_from_workflows_b1cc.prompt import GenerateCriteriaFromWorkflowsB1ccPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "tools": [
                {
                        "name": AddApplicationResource3968ToolConfig.get_tool_name()
                }
        ],
        "memory_tags": [
                "generating_criteria_from_workflows"
        ],
        "input": {
                "local_fs": [
                        "src/main/java/com/java_template/application/entity/{EntityName}.java",
                        "src/main/java/com/java_template/application/workflow/{EntityName}.json",
                        "src/main/java/com/java_template/prototype/functional_requirement.md"
                ]
        },
        "messages": [
                {
                        "role": "user",
                        "content_from_file": GenerateCriteriaFromWorkflowsB1ccPromptConfig.get_name()
                }
        ]
}
