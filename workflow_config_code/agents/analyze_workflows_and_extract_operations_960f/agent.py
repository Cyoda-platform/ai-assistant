"""
AnalyzeWorkflowsAndExtractOperations960fAgentConfig Agent

Generated from config: workflow_configs/agents/analyze_workflows_and_extract_operations_960f/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class AnalyzeWorkflowsAndExtractOperations960fAgentConfig(AgentProcessor):
    """Agent configuration for analyze_workflows_and_extract_operations_960f"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{AnalyzeWorkflowsAndExtractOperations960fAgentConfig.get_type()}.analyze_workflows_and_extract_operations_960f"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
analyze_workflows_and_extract_operations_960f_agent = AnalyzeWorkflowsAndExtractOperations960fAgentConfig()
