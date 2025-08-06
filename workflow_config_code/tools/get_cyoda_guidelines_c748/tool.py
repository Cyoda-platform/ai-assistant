"""
GetCyodaGuidelinesC748ToolConfig Tool

Generated from config: workflow_configs/tools/get_cyoda_guidelines_c748/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class GetCyodaGuidelinesC748ToolConfig(FunctionProcessor):
    """Tool configuration for get_cyoda_guidelines_c748"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{GetCyodaGuidelinesC748ToolConfig.get_type()}.get_cyoda_guidelines_c748"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "get_cyoda_guidelines_c748"


# Create singleton instance
get_cyoda_guidelines_c748_tool = GetCyodaGuidelinesC748ToolConfig()
