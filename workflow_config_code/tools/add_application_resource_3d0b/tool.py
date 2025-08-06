"""
AddApplicationResource3d0bToolConfig Tool

Generated from config: workflow_configs/tools/add_application_resource_3d0b/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class AddApplicationResource3d0bToolConfig(FunctionProcessor):
    """Tool configuration for add_application_resource_3d0b"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{AddApplicationResource3d0bToolConfig.get_type()}.add_application_resource_3d0b"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "add_application_resource_3d0b"


# Create singleton instance
add_application_resource_3d0b_tool = AddApplicationResource3d0bToolConfig()
