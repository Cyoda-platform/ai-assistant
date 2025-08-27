"""
CheckScheduledEntityStatus4d37ToolConfig Tool

Generated from config: workflow_configs/tools/check_scheduled_entity_status_4d37/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class CheckScheduledEntityStatus4d37ToolConfig(FunctionProcessor):
    """Tool configuration for check_scheduled_entity_status_4d37"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{CheckScheduledEntityStatus4d37ToolConfig.get_type()}.check_scheduled_entity_status_4d37"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "check_scheduled_entity_status_4d37"


# Create singleton instance
check_scheduled_entity_status_4d37_tool = CheckScheduledEntityStatus4d37ToolConfig()
