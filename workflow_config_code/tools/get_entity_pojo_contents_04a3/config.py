"""
GetEntityPojoContents04a3ToolConfig Configuration

Generated from config: workflow_configs/tools/get_entity_pojo_contents_04a3/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "get_entity_pojo_contents",
                "description": "Get entity POJO contents to understand the data model and available properties",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "entity_name": {
                                        "type": "string",
                                        "description": "Name of the entity to get POJO contents"
                                }
                        },
                        "required": [
                                "entity_name"
                        ],
                        "additionalProperties": False
                }
        }
}
