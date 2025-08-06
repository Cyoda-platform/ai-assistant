"""
SaveEnvFileD2aaToolConfig Tool

Generated from config: workflow_configs/tools/save_env_file_d2aa/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class SaveEnvFileD2aaToolConfig(FunctionProcessor):
    """Tool configuration for save_env_file_d2aa"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{SaveEnvFileD2aaToolConfig.get_type()}.save_env_file_d2aa"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "save_env_file_d2aa"


# Create singleton instance
save_env_file_d2aa_tool = SaveEnvFileD2aaToolConfig()
