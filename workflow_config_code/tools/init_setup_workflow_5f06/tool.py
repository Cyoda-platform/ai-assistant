"""
InitSetupWorkflow5f06ToolConfig Tool

Generated from config: workflow_configs/tools/init_setup_workflow_5f06/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class InitSetupWorkflow5f06ToolConfig(FunctionProcessor):
    """Tool configuration for init_setup_workflow_5f06"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{InitSetupWorkflow5f06ToolConfig.get_type()}.init_setup_workflow_5f06"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "init_setup_workflow_5f06"


# Create singleton instance
init_setup_workflow_5f06_tool = InitSetupWorkflow5f06ToolConfig()
