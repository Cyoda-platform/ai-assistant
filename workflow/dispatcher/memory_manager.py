import logging
from typing import List, Optional

import common.config.const as const
from common.config.config import config as env_config
from common.utils.utils import get_current_timestamp_num
from entity.model import ChatMemory, AIMessage, FlowEdgeMessage

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Handles chat memory management, AI message storage, and edge message operations.
    """
    
    def __init__(self, entity_service, cyoda_auth_service):
        """
        Initialize the memory manager.
        
        Args:
            entity_service: Service for entity operations
            cyoda_auth_service: Authentication service
        """
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
    
    async def get_chat_memory(self, memory_id: str) -> ChatMemory:
        """
        Retrieve chat memory by ID.
        
        Args:
            memory_id: ID of the chat memory to retrieve
            
        Returns:
            ChatMemory object
        """
        return await self.entity_service.get_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_MEMORY.value,
            entity_version=env_config.ENTITY_VERSION,
            technical_id=memory_id
        )
    
    async def update_chat_memory(self, memory_id: str, chat_memory: ChatMemory) -> None:
        """
        Update chat memory.
        
        Args:
            memory_id: ID of the chat memory to update
            chat_memory: Updated ChatMemory object
        """
        await self.entity_service.update_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.CHAT_MEMORY.value,
            entity_version=env_config.ENTITY_VERSION,
            technical_id=memory_id,
            entity=chat_memory,
            meta={const.TransitionKey.UPDATE.value: "UPDATE"}
        )
    
    async def append_to_ai_memory(self, entity, content: str, memory_tags: Optional[List[str]] = None) -> None:
        """
        Append content to AI memory.
        
        Args:
            entity: Entity with memory_id
            content: Content to append
            memory_tags: Optional memory tags
        """
        chat_memory = await self.get_chat_memory(memory_id=entity.memory_id)
        edge_message_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
            entity_version=env_config.ENTITY_VERSION,
            entity=AIMessage(role="assistant", content=content),
            meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
        )

        tags = memory_tags or [env_config.GENERAL_MEMORY_TAG]
        for tag in tags:
            if not chat_memory.messages:
                chat_memory.messages = {}
            chat_memory.messages.setdefault(tag, []).append(AIMessage(edge_message_id=edge_message_id))

        await self.update_chat_memory(memory_id=entity.memory_id, chat_memory=chat_memory)
    
    async def add_edge_message(self, message: FlowEdgeMessage, flow: List[FlowEdgeMessage], user_id: str) -> FlowEdgeMessage:
        """
        Add an edge message to the flow.
        
        Args:
            message: FlowEdgeMessage to add
            flow: List of flow edge messages
            user_id: User ID
            
        Returns:
            Created FlowEdgeMessage with edge_message_id
        """
        edge_message_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
            entity_version=env_config.ENTITY_VERSION,
            entity=message,
            meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
        )
        
        flow_edge_message = FlowEdgeMessage(
            type=message.type,
            publish=message.publish,
            edge_message_id=edge_message_id,
            last_modified=message.last_modified,
            user_id=user_id
        )
        flow.append(flow_edge_message)
        return flow_edge_message
    
    async def get_ai_memory_messages(self, memory: ChatMemory, memory_tags: List[str]) -> List[AIMessage]:
        """
        Retrieve AI memory messages for given tags.
        
        Args:
            memory: ChatMemory object
            memory_tags: List of memory tags to retrieve
            
        Returns:
            List of AIMessage objects
        """
        messages = []
        for memory_tag in memory_tags:
            entity_messages: List[AIMessage] = memory.messages.get(memory_tag, [])
            for entity_message in entity_messages:
                message_content = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
                    entity_version=env_config.ENTITY_VERSION,
                    technical_id=entity_message.edge_message_id,
                    meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                )
                messages.append(message_content)
        return messages
    
    async def store_ai_response(self, response: str, memory: ChatMemory, memory_tags: List[str]) -> None:
        """
        Store AI agent response in memory.
        
        Args:
            response: AI response content
            memory: ChatMemory object
            memory_tags: Memory tags to store under
        """
        edge_message_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
            entity_version=env_config.ENTITY_VERSION,
            entity=AIMessage(role="assistant", content=response),
            meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
        )
        
        for memory_tag in memory_tags:
            memory.messages.get(memory_tag, []).append(AIMessage(edge_message_id=edge_message_id))
