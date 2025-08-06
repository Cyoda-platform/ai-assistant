"""
NotStageCompleted41d2ToolConfig Tool

Generated from config: workflow_configs/tools/not_stage_completed_41d2/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class NotStageCompleted41d2ToolConfig(FunctionProcessor):
    """Tool configuration for not_stage_completed_41d2"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{NotStageCompleted41d2ToolConfig.get_type()}.not_stage_completed_41d2"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "not_stage_completed_41d2"


# Create singleton instance
not_stage_completed_41d2_tool = NotStageCompleted41d2ToolConfig()
