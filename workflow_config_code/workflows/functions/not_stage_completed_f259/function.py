"""
NotStageCompletedF259FunctionConfig Function

Generated from config: workflow_configs/functions/not_stage_completed_f259/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class NotStageCompletedF259FunctionConfig(FunctionProcessor):
    """Function configuration for not_stage_completed_f259"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{NotStageCompletedF259FunctionConfig.get_type()}.not_stage_completed_f259"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "not_stage_completed_f259"


# Create singleton instance
not_stage_completed_f259_function = NotStageCompletedF259FunctionConfig()
