"""
TriggerParentEntityB4c4FunctionConfig Function

Generated from config: workflow_configs/functions/trigger_parent_entity_b4c4/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class TriggerParentEntityB4c4FunctionConfig(FunctionProcessor):
    """Function configuration for trigger_parent_entity_b4c4"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{TriggerParentEntityB4c4FunctionConfig.get_type()}.trigger_parent_entity_b4c4"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "trigger_parent_entity_b4c4"


# Create singleton instance
trigger_parent_entity_b4c4_function = TriggerParentEntityB4c4FunctionConfig()
