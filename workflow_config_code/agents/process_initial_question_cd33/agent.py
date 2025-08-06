"""
ProcessInitialQuestionCd33AgentConfig Agent

Generated from config: workflow_configs/agents/process_initial_question_cd33/agent.json
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class ProcessInitialQuestionCd33AgentConfig(AgentProcessor):
    """Agent configuration for process_initial_question_cd33"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{ProcessInitialQuestionCd33AgentConfig.get_type()}.process_initial_question_cd33"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {})


# Create singleton instance
process_initial_question_cd33_agent = ProcessInitialQuestionCd33AgentConfig()
