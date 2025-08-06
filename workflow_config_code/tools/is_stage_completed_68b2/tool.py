"""
IsStageCompleted68b2ToolConfig Tool

Generated from config: workflow_configs/tools/is_stage_completed_68b2/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class IsStageCompleted68b2ToolConfig(FunctionProcessor):
    """Tool configuration for is_stage_completed_68b2"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{IsStageCompleted68b2ToolConfig.get_type()}.is_stage_completed_68b2"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "is_stage_completed_68b2"


# Create singleton instance
is_stage_completed_68b2_tool = IsStageCompleted68b2ToolConfig()
