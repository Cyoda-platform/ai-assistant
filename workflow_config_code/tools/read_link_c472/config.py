"""
ReadLinkC472ToolConfig Configuration

Generated from config: workflow_configs/tools/read_link_c472/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "read_link",
                "description": "Read content from a URL. Use this function when you need to fetch content from a web resource. For example, if the user wants to add data sources for an API and provides an exact link, you should first read the link contents before proceeding with analysis.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "url": {
                                        "type": "string"
                                }
                        },
                        "required": [
                                "url"
                        ],
                        "additionalProperties": False
                }
        }
}
