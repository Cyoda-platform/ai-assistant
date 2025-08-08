"""
GenerateWorkflowOrchestratorsG7h8ToolConfig Configuration

Configuration data for the generate workflow orchestrators tool.
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
                "workflow_directory_path": "src/main/java/com/java_template/application/workflow"
            }
        }
    }
