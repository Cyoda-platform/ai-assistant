"""
DeployCyodaEnv76b1ToolConfig Tool

Generated from config: workflow_configs/tools/deploy_cyoda_env_76b1/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class DeployCyodaEnv76b1ToolConfig(FunctionProcessor):
    """Tool configuration for deploy_cyoda_env_76b1"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{DeployCyodaEnv76b1ToolConfig.get_type()}.deploy_cyoda_env_76b1"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "deploy_cyoda_env_76b1"


# Create singleton instance
deploy_cyoda_env_76b1_tool = DeployCyodaEnv76b1ToolConfig()
