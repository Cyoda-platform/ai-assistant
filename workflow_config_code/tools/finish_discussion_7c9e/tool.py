"""
FinishDiscussion7c9eToolConfig Tool

Generated from config: workflow_configs/tools/finish_discussion_7c9e/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class FinishDiscussion7c9eToolConfig(FunctionProcessor):
    """Tool configuration for finish_discussion_7c9e"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{FinishDiscussion7c9eToolConfig.get_type()}.finish_discussion_7c9e"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "finish_discussion_7c9e"


# Create singleton instance
finish_discussion_7c9e_tool = FinishDiscussion7c9eToolConfig()
