"""
NotStageCompleted6d2bToolConfig Tool

Generated from config: workflow_configs/tools/not_stage_completed_6d2b/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class NotStageCompleted6d2bToolConfig(FunctionProcessor):
    """Tool configuration for not_stage_completed_6d2b"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{NotStageCompleted6d2bToolConfig.get_type()}.not_stage_completed_6d2b"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "not_stage_completed_6d2b"


# Create singleton instance
not_stage_completed_6d2b_tool = NotStageCompleted6d2bToolConfig()
