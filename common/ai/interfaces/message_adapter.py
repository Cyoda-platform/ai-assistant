"""
Message adapter interface for AI Agents.

Defines the contract for converting between different message formats
used in the AI assistant system and various AI agent SDKs (OpenAI, Google ADK, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from entity.model import AIMessage


class MessageAdapterInterface(ABC):
    """
    Abstract interface for message format adaptation.
    
    Handles conversion between AIMessage objects and the standard
    message format expected by different AI agent SDKs.
    """

    @abstractmethod
    def adapt_messages(self, messages: List[AIMessage]) -> List[Dict[str, str]]:
        """
        Convert AIMessage objects to standard message format.
        
        Args:
            messages: List of AIMessage objects to convert
            
        Returns:
            List of dictionaries with 'role' and 'content' keys
        """
        pass

    @abstractmethod
    def validate_message_format(self, message: Dict[str, str]) -> bool:
        """
        Validate that a message has the correct format.
        
        Args:
            message: Message dictionary to validate
            
        Returns:
            True if message format is valid, False otherwise
        """
        pass

    @abstractmethod
    def create_default_message(self) -> Dict[str, str]:
        """
        Create a default message when no messages are provided.
        
        Returns:
            Default message dictionary
        """
        pass
