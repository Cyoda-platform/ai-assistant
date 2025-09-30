"""
CloneRepoB60aFunctionConfig Function

Generated from config: workflow_configs/functions/clone_repo_b60a/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class CloneRepoB60aFunctionConfig(FunctionProcessor):
    """Function configuration for clone_repo_b60a"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{CloneRepoB60aFunctionConfig.get_type()}.clone_repo_b60a"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "clone_repo_b60a"


# Create singleton instance
clone_repo_b60a_function = CloneRepoB60aFunctionConfig()
