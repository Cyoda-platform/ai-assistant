"""
AnalyzeWorkflowsAndExtractOperations960fAgentConfig Configuration

Generated from config: workflow_configs/agents/analyze_workflows_and_extract_operations_960f/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_application_resource_3968.tool import AddApplicationResource3968ToolConfig
from workflow_config_code.prompts.analyze_workflows_and_extract_operations_f28d.prompt import AnalyzeWorkflowsAndExtractOperationsF28dPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "input": {
                "local_fs": [
                        "src/main/java/com/java_template/application/entity/{EntityName}.java",
                        "src/main/java/com/java_template/application/workflow/{EntityName}.json",
                        "src/main/java/com/java_template/application/workflow_prototypes/{EntityName}.txt",
                        "src/main/java/com/java_template/prototype/functional_requirement.md"
                ]
        },
        "memory_tags": [
                "processors_generation"
        ],
        "tools": [
                {
                        "name": AddApplicationResource3968ToolConfig.get_tool_name()
                }
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": AnalyzeWorkflowsAndExtractOperationsF28dPromptConfig.get_name()
                }
        ]
}
