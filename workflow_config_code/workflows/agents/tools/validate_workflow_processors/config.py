"""
ValidateWorkflowProcessorsToolConfig Configuration

Generated from config: workflow_configs/agents/tools/validate_workflow_processors/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "validate_workflow_processors",
                "description": "Validate presence of all processors and criteria referenced in workflow configurations",
                "parameters": {
                        "type": "object",
                        "properties": {
                                "workflow_directory": {
                                        "type": "string",
                                        "description": "Directory containing workflow JSON files"
                                },
                                "processor_directory": {
                                        "type": "string",
                                        "description": "Directory containing processor Java files"
                                },
                                "criteria_directory": {
                                        "type": "string",
                                        "description": "Directory containing criteria Java files"
                                }
                        },
                        "required": [
                                "workflow_directory",
                                "processor_directory",
                                "criteria_directory"
                        ]
                }
        }
}
