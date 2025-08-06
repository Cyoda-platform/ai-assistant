"""
ListDirectoryFiles6ec5ToolConfig Configuration

Generated from config: workflow_configs/tools/list_directory_files_6ec5/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "list_directory_files",
                "description": "List all files in a directory to see what processors, criteria, or entities were created",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "directory_path": {
                                        "type": "string",
                                        "description": "Path to the directory to list.",
                                        "enum": [
                                                "src/main/java/com/java_template/application/entity"
                                        ]
                                }
                        },
                        "required": [
                                "directory_path"
                        ],
                        "additionalProperties": False
                }
        }
}
