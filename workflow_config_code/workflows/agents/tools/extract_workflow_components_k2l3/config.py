"""
ExtractWorkflowComponentsK2l3ToolConfig Configuration

Generated from config: workflow_configs/agents/tools/extract_workflow_components_k2l3/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "extract_workflow_components",
                "description": "Extract all processor names and criteria function names from workflow configurations",
                "parameters": {
                        "type": "object",
                        "properties": {
                                "workflow_directory": {
                                        "type": "string",
                                        "description": "Directory containing workflow JSON files to analyze"
                                },
                                "output_format": {
                                        "type": "string",
                                        "enum": [
                                                "detailed",
                                                "summary",
                                                "list"
                                        ],
                                        "description": "Format of the output: detailed (full analysis), summary (counts and lists), list (simple lists)"
                                }
                        },
                        "required": [
                                "workflow_directory"
                        ]
                }
        }
}
