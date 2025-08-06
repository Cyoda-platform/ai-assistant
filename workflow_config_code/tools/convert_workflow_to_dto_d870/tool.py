"""
ConvertWorkflowToDtoD870ToolConfig Tool

Generated from config: workflow_configs/tools/convert_workflow_to_dto_d870/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class ConvertWorkflowToDtoD870ToolConfig(FunctionProcessor):
    """Tool configuration for convert_workflow_to_dto_d870"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ConvertWorkflowToDtoD870ToolConfig.get_type()}.convert_workflow_to_dto_d870"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "convert_workflow_to_dto_d870"


# Create singleton instance
convert_workflow_to_dto_d870_tool = ConvertWorkflowToDtoD870ToolConfig()
