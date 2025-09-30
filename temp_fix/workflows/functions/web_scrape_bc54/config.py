"""
WebScrapeBc54ToolConfig Configuration

Generated from config: workflow_configs/tools/web_scrape_bc54/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "web_scrape",
                "description": "Scrape content from a webpage using a CSS selector. Use this function when you need to scrape online content. For example, if the user wants to add data sources for an API and provides an exact link for web scraping, you should scrape the resource before analyzing the question.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "url": {
                                        "type": "string"
                                },
                                "selector": {
                                        "type": "string"
                                }
                        },
                        "required": [
                                "url",
                                "selector"
                        ],
                        "additionalProperties": False
                }
        }
}
