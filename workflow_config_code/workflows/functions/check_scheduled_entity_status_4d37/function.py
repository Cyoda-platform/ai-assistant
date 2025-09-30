"""
CheckScheduledEntityStatus4d37FunctionConfig Function

Generated from config: workflow_configs/functions/check_scheduled_entity_status_4d37/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class CheckScheduledEntityStatus4d37FunctionConfig(FunctionProcessor):
    """Function configuration for check_scheduled_entity_status_4d37"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{CheckScheduledEntityStatus4d37FunctionConfig.get_type()}.check_scheduled_entity_status_4d37"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "check_scheduled_entity_status_4d37"


# Create singleton instance
check_scheduled_entity_status_4d37_function = CheckScheduledEntityStatus4d37FunctionConfig()
