"""
SaveEnvFileD2aaFunctionConfig Function

Generated from config: workflow_configs/functions/save_env_file_d2aa/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class SaveEnvFileD2aaFunctionConfig(FunctionProcessor):
    """Function configuration for save_env_file_d2aa"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{SaveEnvFileD2aaFunctionConfig.get_type()}.save_env_file_d2aa"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "save_env_file_d2aa"


# Create singleton instance
save_env_file_d2aa_function = SaveEnvFileD2aaFunctionConfig()
