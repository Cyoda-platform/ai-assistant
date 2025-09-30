"""
AddNewWorkflowA537ToolConfig Tool

Generated from config: workflow_configs/tools/add_new_workflow_a537/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class AddNewWorkflowA537ToolConfig(FunctionProcessor):
    """Tool configuration for add_new_workflow_a537"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{AddNewWorkflowA537ToolConfig.get_type()}.add_new_workflow_a537"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "add_new_workflow_a537"


# Create singleton instance
add_new_workflow_a537_tool = AddNewWorkflowA537ToolConfig()
