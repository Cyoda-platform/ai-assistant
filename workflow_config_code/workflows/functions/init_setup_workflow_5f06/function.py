"""
InitSetupWorkflow5f06FunctionConfig Function

Generated from config: workflow_configs/functions/init_setup_workflow_5f06/function.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class InitSetupWorkflow5f06FunctionConfig(FunctionProcessor):
    """Function configuration for init_setup_workflow_5f06"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{InitSetupWorkflow5f06FunctionConfig.get_type()}.init_setup_workflow_5f06"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get function configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_function_name() -> str:
        """Get the function name without processor type"""
        return "init_setup_workflow_5f06"


# Create singleton instance
init_setup_workflow_5f06_function = InitSetupWorkflow5f06FunctionConfig()
