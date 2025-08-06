"""
Core Interfaces for Workflow Best UX

Complete interface hierarchy:
- AIConfig sub-interfaces: AgentConfig, ToolConfig, MessageConfig, PromptConfig
- Processor interfaces: AgentProcessor, MessageProcessor, FunctionProcessor
- Builder interfaces for each config type
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


# Base AIConfig interface
class AIConfig(ABC):
    """Base interface for all AI configuration components"""

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Get the static name of this component"""
        pass


# AIConfig sub-interfaces
class AgentConfig(AIConfig):
    """Configuration interface for agents"""

    @abstractmethod
    def get_tools(self) -> List['ToolConfig']:
        """Get list of tool configurations"""
        pass

    @abstractmethod
    def get_prompts(self) -> List['PromptConfig']:
        """Get list of prompt configurations"""
        pass


class ToolConfig(AIConfig):
    """Configuration interface for tools"""

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get tool parameters"""
        pass


class MessageConfig(AIConfig):
    """Configuration interface for messages"""

    @abstractmethod
    def get_content(self) -> str:
        """Get message content"""
        pass


class PromptConfig(AIConfig):
    """Configuration interface for prompts"""

    @abstractmethod
    def get_content(self) -> str:
        """Get prompt content"""
        pass


# Processor interfaces
class Processor(ABC):
    """Base interface for all processors"""

    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the given context and return results"""
        pass


class AgentProcessor(Processor):
    """Interface for agent processors"""

    @abstractmethod
    def get_config(self) -> AgentConfig:
        """Get agent configuration"""
        pass


class MessageProcessor(Processor):
    """Interface for message processors"""

    @abstractmethod
    def get_config(self) -> MessageConfig:
        """Get message configuration"""
        pass


class FunctionProcessor(Processor):
    """Interface for function processors (tools)"""

    @abstractmethod
    def get_config(self) -> ToolConfig:
        """Get tool configuration"""
        pass
