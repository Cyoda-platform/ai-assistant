"""
AddApplicationResource3d0bToolConfig Configuration

Generated from config: workflow_configs/tools/add_application_resource_3d0b/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
            "name": "add_application_resource",
            "description": "Add application resource file with path and content",
            "parameters": {
                "type": "object",
                "properties": {
                    "resource_path": {
                        "type": "string",
                        "description": "Full relative path to the resource including filename"
                    },
                    "file_contents": {
                        "type": "string",
                        "description": "Content of the file to be written"
                    }
                },
                "required": [
                    "resource_path",
                    "file_contents"
                ]
            }
        }
    }
