# Processor interfaces - unified with dispatcher processors
from abc import ABC, abstractmethod
from typing import Dict, Any

# Import the unified processors from dispatcher
from workflow.dispatcher.processors import (
    Processor as BaseProcessor,
    AgentProcessor as BaseAgentProcessor,
    ConfigBasedAgentProcessor,
    FunctionProcessor as BaseFunctionProcessor,
    MessageProcessor as BaseMessageProcessor
)


class Processor(BaseProcessor):
    """Unified base interface for all processors"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the given context and return results - backward compatibility method"""
        # This method provides backward compatibility for the old interface
        # Subclasses can override this or use the new execute() method
        pass


class AgentProcessor(BaseAgentProcessor):
    """Unified interface for agent processors"""

    @staticmethod
    def get_type() -> str:
        """Get processor type"""
        return "AgentProcessor"


class MessageProcessor(BaseMessageProcessor):
    """Unified interface for message processors"""

    @staticmethod
    def get_type() -> str:
        """Get processor type"""
        return "MessageProcessor"


class FunctionProcessor(BaseFunctionProcessor):
    """Unified interface for function processors (tools)"""

    @staticmethod
    def get_type() -> str:
        """Get processor type"""
        return "FunctionProcessor"
