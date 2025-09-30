"""
WebSearch53beToolConfig Configuration

Generated from config: workflow_configs/tools/web_search_53be/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "web_search",
                "description": "Search the web using Google Custom Search API. Use this function when you need to formulate questions or requirements for information to be searched online. For example, if the user wants to add data sources for an API but does not provide an exact link or documentation.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "query": {
                                        "type": "string"
                                }
                        },
                        "required": [
                                "query"
                        ],
                        "additionalProperties": False
                }
        }
}
