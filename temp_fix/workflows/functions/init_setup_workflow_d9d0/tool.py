"""
InitSetupWorkflowD9d0ToolConfig Tool

Generated from config: workflow_configs/tools/init_setup_workflow_d9d0/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class InitSetupWorkflowD9d0ToolConfig(FunctionProcessor):
    """Tool configuration for init_setup_workflow_d9d0"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{InitSetupWorkflowD9d0ToolConfig.get_type()}.init_setup_workflow_d9d0"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "init_setup_workflow_d9d0"


# Create singleton instance
init_setup_workflow_d9d0_tool = InitSetupWorkflowD9d0ToolConfig()
