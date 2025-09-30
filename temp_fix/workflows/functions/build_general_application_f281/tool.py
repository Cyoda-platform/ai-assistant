"""
BuildGeneralApplicationF281ToolConfig Tool

Generated from config: workflow_configs/tools/build_general_application_f281/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class BuildGeneralApplicationF281ToolConfig(FunctionProcessor):
    """Tool configuration for build_general_application_f281"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{BuildGeneralApplicationF281ToolConfig.get_type()}.build_general_application_f281"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "build_general_application_f281"


# Create singleton instance
build_general_application_f281_tool = BuildGeneralApplicationF281ToolConfig()
