"""
ValidateWorkflowProcessorsToolConfig Tool

Generated from config: workflow_configs/agents/tools/validate_workflow_processors/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ValidateWorkflowProcessorsToolConfig(FunctionProcessor):
    """Tool configuration for validate_workflow_processors"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ValidateWorkflowProcessorsToolConfig.get_type()}.validate_workflow_processors"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "validate_workflow_processors"


# Create singleton instance
validate_workflow_processors_tool = ValidateWorkflowProcessorsToolConfig()
