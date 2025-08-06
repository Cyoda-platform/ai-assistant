"""
NotStageCompleted5e0eToolConfig Tool

Generated from config: workflow_configs/tools/not_stage_completed_5e0e/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class NotStageCompleted5e0eToolConfig(FunctionProcessor):
    """Tool configuration for not_stage_completed_5e0e"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{NotStageCompleted5e0eToolConfig.get_type()}.not_stage_completed_5e0e"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "not_stage_completed_5e0e"


# Create singleton instance
not_stage_completed_5e0e_tool = NotStageCompleted5e0eToolConfig()
