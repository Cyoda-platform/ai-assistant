"""
IsStageCompletedE0d9FunctionConfig Function

Generated from config: workflow_configs/functions/is_stage_completed_e0d9/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class IsStageCompletedE0d9FunctionConfig(FunctionProcessor):
    """Function configuration for is_stage_completed_e0d9"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{IsStageCompletedE0d9FunctionConfig.get_type()}.is_stage_completed_e0d9"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "is_stage_completed_e0d9"


# Create singleton instance
is_stage_completed_e0d9_function = IsStageCompletedE0d9FunctionConfig()
