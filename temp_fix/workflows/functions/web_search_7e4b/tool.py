"""
WebSearch7e4bToolConfig Tool

Generated from config: workflow_configs/tools/web_search_7e4b/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class WebSearch7e4bToolConfig(FunctionProcessor):
    """Tool configuration for web_search_7e4b"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{WebSearch7e4bToolConfig.get_type()}.web_search_7e4b"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "web_search_7e4b"


# Create singleton instance
web_search_7e4b_tool = WebSearch7e4bToolConfig()
