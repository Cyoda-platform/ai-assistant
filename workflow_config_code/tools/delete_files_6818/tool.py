"""
DeleteFiles6818ToolConfig Tool

Generated from config: workflow_configs/tools/delete_files_6818/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class DeleteFiles6818ToolConfig(FunctionProcessor):
    """Tool configuration for delete_files_6818"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{DeleteFiles6818ToolConfig.get_type()}.delete_files_6818"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "delete_files_6818"


# Create singleton instance
delete_files_6818_tool = DeleteFiles6818ToolConfig()
