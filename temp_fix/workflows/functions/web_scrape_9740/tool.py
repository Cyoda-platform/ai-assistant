"""
WebScrape9740ToolConfig Tool

Generated from config: workflow_configs/tools/web_scrape_9740/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class WebScrape9740ToolConfig(FunctionProcessor):
    """Tool configuration for web_scrape_9740"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{WebScrape9740ToolConfig.get_type()}.web_scrape_9740"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "web_scrape_9740"


# Create singleton instance
web_scrape_9740_tool = WebScrape9740ToolConfig()
