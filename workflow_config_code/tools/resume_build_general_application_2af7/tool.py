"""
ResumeBuildGeneralApplication2af7ToolConfig Tool

Generated from config: workflow_configs/tools/resume_build_general_application_2af7/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ResumeBuildGeneralApplication2af7ToolConfig(FunctionProcessor):
    """Tool configuration for resume_build_general_application_2af7"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ResumeBuildGeneralApplication2af7ToolConfig.get_type()}.resume_build_general_application_2af7"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "resume_build_general_application_2af7"


# Create singleton instance
resume_build_general_application_2af7_tool = ResumeBuildGeneralApplication2af7ToolConfig()
