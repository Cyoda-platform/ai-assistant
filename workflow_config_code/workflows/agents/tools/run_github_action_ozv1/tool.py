"""
RunGithubActionOzv1ToolConfig Tool

Generated from config: workflow_configs/agents/tools/run_github_action_ozv1/tool.json
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class RunGithubActionOzv1ToolConfig(FunctionProcessor):
    """Tool configuration for run_github_action_ozv1"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{RunGithubActionOzv1ToolConfig.get_type()}.run_github_action_ozv1"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "run_github_action_ozv1"


# Create singleton instance
run_github_action_ozv1_tool = RunGithubActionOzv1ToolConfig()
