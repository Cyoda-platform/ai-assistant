"""
DeleteFiles6818FunctionConfig Function

Generated from config: workflow_configs/functions/delete_files_6818/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class DeleteFiles6818FunctionConfig(FunctionProcessor):
    """Function configuration for delete_files_6818"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{DeleteFiles6818FunctionConfig.get_type()}.delete_files_6818"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "delete_files_6818"


# Create singleton instance
delete_files_6818_function = DeleteFiles6818FunctionConfig()
