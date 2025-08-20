"""Memory Management Interface for workflow dispatcher."""

from abc import ABC, abstractmethod
from entity.model import ChatMemory


class MemoryManager(ABC):
    """Interface for memory management strategies"""
    
    @abstractmethod
    async def get_chat_memory(self, memory_id: str) -> ChatMemory:
        """
        Retrieve chat memory by ID.
        
        Args:
            memory_id: Unique identifier for the chat memory
            
        Returns:
            ChatMemory object
        """
        pass
    
    @abstractmethod
    async def update_chat_memory(self, memory_id: str, chat_memory: ChatMemory) -> None:
        """
        Update chat memory.
        
        Args:
            memory_id: Unique identifier for the chat memory
            chat_memory: Updated ChatMemory object
        """
        pass
