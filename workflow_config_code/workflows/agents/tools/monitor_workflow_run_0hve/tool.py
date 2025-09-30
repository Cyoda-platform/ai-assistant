"""
MonitorWorkflowRun0hveToolConfig Tool

Generated from config: workflow_configs/agents/tools/monitor_workflow_run_0hve/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class MonitorWorkflowRun0hveToolConfig(FunctionProcessor):
    """Tool configuration for monitor_workflow_run_0hve"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{MonitorWorkflowRun0hveToolConfig.get_type()}.monitor_workflow_run_0hve"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "monitor_workflow_run_0hve"


# Create singleton instance
monitor_workflow_run_0hve_tool = MonitorWorkflowRun0hveToolConfig()
