"""
GetEntityPojoContents04a3ToolConfig Tool

Generated from config: workflow_configs/tools/get_entity_pojo_contents_04a3/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class GetEntityPojoContents04a3ToolConfig(FunctionProcessor):
    """Tool configuration for get_entity_pojo_contents_04a3"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{GetEntityPojoContents04a3ToolConfig.get_type()}.get_entity_pojo_contents_04a3"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "get_entity_pojo_contents_04a3"


# Create singleton instance
get_entity_pojo_contents_04a3_tool = GetEntityPojoContents04a3ToolConfig()
