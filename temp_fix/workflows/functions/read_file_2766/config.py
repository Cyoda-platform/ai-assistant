"""
ReadFile2766ToolConfig Configuration

Generated from config: workflow_configs/tools/read_file_2766/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "read_file",
                "description": "Read the contents of a file.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "filename": {
                                        "type": "string"
                                }
                        },
                        "required": [
                                "filename"
                        ],
                        "additionalProperties": False
                }
        }
}
