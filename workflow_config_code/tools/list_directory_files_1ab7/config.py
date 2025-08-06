"""
ListDirectoryFiles1ab7ToolConfig Configuration

Generated from config: workflow_configs/tools/list_directory_files_1ab7/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "list_directory_files",
                "description": "List all files in 'src/main/java/com/java_template/application/entity' to get the list of entities created",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "directory_path": {
                                        "type": "string"
                                }
                        },
                        "required": [
                                "directory_path"
                        ],
                        "additionalProperties": False
                }
        }
}
