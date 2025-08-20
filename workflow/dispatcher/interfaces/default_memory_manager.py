"""Default Memory Manager implementation wrapping existing memory manager."""

from entity.model import ChatMemory
from .memory_manager import MemoryManager


class DefaultMemoryManager(MemoryManager):
    """Default memory manager that wraps the existing memory manager from services"""
    
    def __init__(self, existing_memory_manager):
        """
        Initialize with existing memory manager.
        
        Args:
            existing_memory_manager: The existing memory manager from services
        """
        self.existing_memory_manager = existing_memory_manager
    
    async def get_chat_memory(self, memory_id: str) -> ChatMemory:
        """
        Retrieve chat memory by ID using existing memory manager.
        
        Args:
            memory_id: Unique identifier for the chat memory
            
        Returns:
            ChatMemory object
        """
        return await self.existing_memory_manager.get_chat_memory(memory_id=memory_id)
    
    async def update_chat_memory(self, memory_id: str, chat_memory: ChatMemory) -> None:
        """
        Update chat memory using existing memory manager.
        
        Args:
            memory_id: Unique identifier for the chat memory
            chat_memory: Updated ChatMemory object
        """
        await self.existing_memory_manager.update_chat_memory(
            memory_id=memory_id, 
            chat_memory=chat_memory
        )
