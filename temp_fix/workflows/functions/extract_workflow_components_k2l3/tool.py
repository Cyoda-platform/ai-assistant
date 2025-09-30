"""
ExtractWorkflowComponentsK2l3ToolConfig Tool

Implements FunctionProcessor interface with get_name() and get_config() methods.
Extracts all processor names and criteria function names from workflow configurations.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ExtractWorkflowComponentsK2l3ToolConfig(FunctionProcessor):
    """Tool configuration for extract_workflow_components_k2l3"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ExtractWorkflowComponentsK2l3ToolConfig.get_type()}.extract_workflow_components_k2l3"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "extract_workflow_components_k2l3"


# Create singleton instance
extract_workflow_components_k2l3_tool = ExtractWorkflowComponentsK2l3ToolConfig()
