"""
ScheduleCloseProcessB2b5ToolConfig Tool

Generated from config: workflow_configs/agents/tools/schedule_close_process_b2b5/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ScheduleCloseProcessB2b5ToolConfig(FunctionProcessor):
    """Tool configuration for schedule_close_process_b2b5"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ScheduleCloseProcessB2b5ToolConfig.get_type()}.schedule_close_process_b2b5"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "schedule_close_process_b2b5"


# Create singleton instance
schedule_close_process_b2b5_tool = ScheduleCloseProcessB2b5ToolConfig()
