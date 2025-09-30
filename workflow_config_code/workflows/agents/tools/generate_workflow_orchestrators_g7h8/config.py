"""
GenerateWorkflowOrchestratorsG7h8ToolConfig Configuration

Generated from config: workflow_configs/agents/tools/generate_workflow_orchestrators_g7h8/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "generate_workflow_orchestrators",
                "description": "Reads workflow JSON files from a directory path and generates Java workflow orchestrators for each workflow with conditional logic for processors and criteria",
                "strict": True,
                "parameters": {
                        "workflow_directory_path": "src/main/resources/workflow"
                }
        }
}
