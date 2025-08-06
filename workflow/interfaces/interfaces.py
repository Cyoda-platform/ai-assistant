# Processor interfaces
from abc import ABC, abstractmethod
from typing import Dict, Any


class Processor(ABC):
    """Base interface for all processors"""

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the given context and return results"""
        pass


class AgentProcessor(Processor):
    """Interface for agent processors"""

    @staticmethod
    def get_type() -> str:
        """Get agent configuration"""
        return "AgentProcessor"


class MessageProcessor(Processor):
    """Interface for message processors"""

    @staticmethod
    def get_type() -> str:
        """Get agent configuration"""
        return "MessageProcessor"


class FunctionProcessor(Processor):
    """Interface for function processors (tools)"""

    @staticmethod
    def get_type() -> str:
        """Get agent configuration"""
        return "FunctionProcessor"
