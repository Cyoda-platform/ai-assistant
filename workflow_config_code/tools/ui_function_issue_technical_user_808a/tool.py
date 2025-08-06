"""
UiFunctionIssueTechnicalUser808aToolConfig Tool

Generated from config: workflow_configs/tools/ui_function_issue_technical_user_808a/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class UiFunctionIssueTechnicalUser808aToolConfig(FunctionProcessor):
    """Tool configuration for ui_function_issue_technical_user_808a"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{UiFunctionIssueTechnicalUser808aToolConfig.get_type()}.ui_function_issue_technical_user_808a"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "ui_function_issue_technical_user_808a"


# Create singleton instance
ui_function_issue_technical_user_808a_tool = UiFunctionIssueTechnicalUser808aToolConfig()
