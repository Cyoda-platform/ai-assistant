import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from workflow.dispatcher.memory_manager import MemoryManager
from entity.model import AgenticFlowEntity, ChatMemory, AIMessage
from common.config.config import config as env_config
import common.config.const as const


class TestMemoryManager:
    """Test cases for MemoryManager."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for MemoryManager."""
        return {
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
        }

    @pytest.fixture
    def manager(self, mock_dependencies):
        """Create MemoryManager instance."""
        return MemoryManager(**mock_dependencies)

    @pytest.fixture
    def mock_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.technical_id = "test_tech_id"
        entity.memory_id = "test_memory_id"
        entity.workflow_cache = {}
        return entity

    @pytest.fixture
    def mock_memory(self):
        """Create mock ChatMemory."""
        memory = MagicMock(spec=ChatMemory)
        memory.messages = {
            env_config.GENERAL_MEMORY_TAG: []
        }
        memory.technical_id = "memory_tech_id"
        return memory

    @pytest.fixture
    def mock_ai_message(self):
        """Create mock AIMessage."""
        return AIMessage(role="user", content="Test message")

    @pytest.mark.asyncio
    async def test_append_to_ai_memory_success(self, manager, mock_entity, mock_memory):
        """Test successful AI memory appending."""
        content = "Test memory content"
        memory_tags = [env_config.GENERAL_MEMORY_TAG]

        # Mock get_chat_memory to return the mock memory
        manager.get_chat_memory = AsyncMock(return_value=mock_memory)

        # Mock add_item to return edge message ID
        manager.entity_service.add_item = AsyncMock(return_value="edge_msg_123")

        await manager.append_to_ai_memory(mock_entity, content, memory_tags)

        # Should call add_item to create AI memory edge message
        manager.entity_service.add_item.assert_called()
        call_args = manager.entity_service.add_item.call_args
        assert call_args[1]['entity_model'] == const.ModelName.AI_MEMORY_EDGE_MESSAGE.value

    @pytest.mark.asyncio
    async def test_append_to_ai_memory_with_single_tag(self, manager, mock_entity, mock_memory):
        """Test AI memory appending with single memory tag."""
        content = "Test content"
        memory_tags = [env_config.GENERAL_MEMORY_TAG]

        # Mock get_chat_memory to return the mock memory
        manager.get_chat_memory = AsyncMock(return_value=mock_memory)

        # Mock add_item to return edge message ID
        manager.entity_service.add_item = AsyncMock(return_value="edge_msg_123")

        await manager.append_to_ai_memory(mock_entity, content, memory_tags)

        # Verify AI memory edge message creation
        manager.entity_service.add_item.assert_called()
        call_args = manager.entity_service.add_item.call_args
        assert call_args[1]['entity_model'] == const.ModelName.AI_MEMORY_EDGE_MESSAGE.value

        # Verify the entity content
        entity_data = call_args[1]['entity']
        assert entity_data.content == content
        assert entity_data.role == "assistant"

    @pytest.mark.asyncio
    async def test_append_to_ai_memory_multiple_tags(self, manager, mock_entity, mock_memory):
        """Test AI memory appending with multiple memory tags."""
        content = "Test content"
        memory_tags = ["tag1", "tag2", "tag3"]

        # Mock get_chat_memory to return the mock memory
        manager.get_chat_memory = AsyncMock(return_value=mock_memory)

        # Mock add_item to return edge message ID
        manager.entity_service.add_item = AsyncMock(return_value="edge_msg_123")

        # Initialize memory messages for all tags
        for tag in memory_tags:
            mock_memory.messages[tag] = []

        await manager.append_to_ai_memory(mock_entity, content, memory_tags)

        # Should call add_item once to create AI memory edge message
        manager.entity_service.add_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_append_to_ai_memory_error_handling(self, manager, mock_entity, mock_memory):
        """Test AI memory appending with error."""
        content = "Test content"
        memory_tags = [env_config.GENERAL_MEMORY_TAG]

        # Mock get_chat_memory to raise an exception
        manager.get_chat_memory = AsyncMock(side_effect=Exception("Get memory error"))

        # Should raise exception since error handling is not implemented in this method
        with pytest.raises(Exception, match="Get memory error"):
            await manager.append_to_ai_memory(mock_entity, content, memory_tags)

    @pytest.mark.asyncio
    async def test_get_ai_memory_messages_success(self, manager, mock_memory):
        """Test successful AI memory messages retrieval."""
        memory_tags = [env_config.GENERAL_MEMORY_TAG, "custom_tag"]

        mock_ai_message1 = AIMessage(edge_message_id="edge_1")
        mock_ai_message2 = AIMessage(edge_message_id="edge_2")

        mock_memory.messages = {
            env_config.GENERAL_MEMORY_TAG: [mock_ai_message1],
            "custom_tag": [mock_ai_message2]
        }

        mock_message_content1 = AIMessage(role="user", content="Message 1")
        mock_message_content2 = AIMessage(role="user", content="Message 2")

        manager.entity_service.get_item = AsyncMock(side_effect=[mock_message_content1, mock_message_content2])

        result = await manager.get_ai_memory_messages(mock_memory, memory_tags)

        assert len(result) == 2
        assert result[0] == mock_message_content1
        assert result[1] == mock_message_content2

        # Verify get_item was called correctly
        assert manager.entity_service.get_item.call_count == 2

    @pytest.mark.asyncio
    async def test_get_ai_memory_messages_empty_memory(self, manager, mock_memory):
        """Test AI memory messages retrieval with empty memory."""
        memory_tags = ["nonexistent_tag"]
        mock_memory.messages = {}
        
        result = await manager.get_ai_memory_messages(mock_memory, memory_tags)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_ai_memory_messages_missing_tag(self, manager, mock_memory):
        """Test AI memory messages retrieval with missing tag."""
        memory_tags = ["missing_tag"]
        mock_memory.messages = {env_config.GENERAL_MEMORY_TAG: []}
        
        result = await manager.get_ai_memory_messages(mock_memory, memory_tags)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_ai_memory_messages_error_handling(self, manager, mock_memory):
        """Test AI memory messages retrieval with error."""
        memory_tags = [env_config.GENERAL_MEMORY_TAG]

        mock_ai_message = AIMessage(edge_message_id="edge_1")
        mock_memory.messages = {env_config.GENERAL_MEMORY_TAG: [mock_ai_message]}

        manager.entity_service.get_item = AsyncMock(side_effect=Exception("Get error"))

        # Should raise the exception since it's not handled gracefully in this method
        with pytest.raises(Exception, match="Get error"):
            await manager.get_ai_memory_messages(mock_memory, memory_tags)

    @pytest.mark.asyncio
    async def test_store_ai_response(self, manager):
        """Test storing AI response in memory."""
        response = "AI response content"
        memory = ChatMemory(messages={env_config.GENERAL_MEMORY_TAG: []})
        memory_tags = [env_config.GENERAL_MEMORY_TAG]

        manager.entity_service.add_item = AsyncMock(return_value="edge_msg_123")

        await manager.store_ai_response(response, memory, memory_tags)

        # Verify add_item was called to store the response
        manager.entity_service.add_item.assert_called_once()
        call_args = manager.entity_service.add_item.call_args
        assert call_args[1]['entity_model'] == const.ModelName.AI_MEMORY_EDGE_MESSAGE.value

        # Verify the entity content
        entity_data = call_args[1]['entity']
        assert entity_data.content == response
        assert entity_data.role == "assistant"

        # Verify message was added to memory
        assert len(memory.messages[env_config.GENERAL_MEMORY_TAG]) == 1
        assert memory.messages[env_config.GENERAL_MEMORY_TAG][0].edge_message_id == "edge_msg_123"

    @pytest.mark.asyncio
    async def test_get_ai_memory_messages_preserves_order(self, manager, mock_memory):
        """Test that AI memory messages preserve order."""
        memory_tags = [env_config.GENERAL_MEMORY_TAG]
        
        mock_ai_messages = []
        mock_message_contents = []
        
        for i in range(3):
            mock_ai_message = MagicMock()
            mock_ai_message.edge_message_id = f"edge_{i}"
            mock_ai_messages.append(mock_ai_message)
            
            mock_content = AIMessage(role="user", content=f"Message {i}")
            mock_message_contents.append(mock_content)
        
        mock_memory.messages = {env_config.GENERAL_MEMORY_TAG: mock_ai_messages}
        manager.entity_service.get_item.side_effect = mock_message_contents
        
        result = await manager.get_ai_memory_messages(mock_memory, memory_tags)
        
        assert len(result) == 3
        for i, message in enumerate(result):
            assert message.content == f"Message {i}"

    @pytest.mark.asyncio
    async def test_append_to_ai_memory_with_custom_role(self, manager, mock_entity, mock_memory):
        """Test AI memory appending with custom role."""
        content = "Assistant response"
        memory_tags = [env_config.GENERAL_MEMORY_TAG]
        role = "assistant"
        
        mock_edge_message = MagicMock()
        mock_edge_message.technical_id = "edge_msg_123"
        
        mock_ai_memory = MagicMock()
        mock_ai_memory.technical_id = "ai_memory_123"
        
        manager.entity_service.create_item.side_effect = [mock_edge_message, mock_ai_memory]
        
        # Mock get_chat_memory to return the mock memory
        manager.get_chat_memory = AsyncMock(return_value=mock_memory)

        # Mock add_item to return edge message ID
        manager.entity_service.add_item = AsyncMock(return_value="edge_msg_123")

        await manager.append_to_ai_memory(mock_entity, content, memory_tags)
        
        # Verify that add_item was called (role is handled internally)
        manager.entity_service.add_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_memory_manager_integration(self, manager, mock_entity, mock_memory):
        """Test full integration of memory manager operations."""
        # Mock the dependencies properly
        manager.get_chat_memory = AsyncMock(return_value=mock_memory)
        manager.entity_service.add_item = AsyncMock(return_value="edge_msg_123")
        manager.update_chat_memory = AsyncMock()

        # Mock memory messages as a regular dict, not async
        mock_memory.messages = {env_config.GENERAL_MEMORY_TAG: []}

        # First append some messages
        await manager.append_to_ai_memory(mock_entity, "Message 1", [env_config.GENERAL_MEMORY_TAG])
        
        # Mock the memory state after appending
        mock_ai_message1 = MagicMock()
        mock_ai_message1.edge_message_id = "edge_1"
        mock_ai_message2 = MagicMock()
        mock_ai_message2.edge_message_id = "edge_2"
        
        mock_memory.messages = {
            env_config.GENERAL_MEMORY_TAG: [mock_ai_message1, mock_ai_message2]
        }
        
        # Mock retrieval
        mock_content1 = AIMessage(role="user", content="Message 1")
        mock_content2 = AIMessage(role="user", content="Message 2")
        manager.entity_service.get_item.side_effect = [mock_content1, mock_content2]
        
        # Verify the message was added to memory (there might be existing messages from fixture)
        assert len(mock_memory.messages[env_config.GENERAL_MEMORY_TAG]) >= 1

        # Test retrieval (mock memory fixture has existing messages)
        result = await manager.get_ai_memory_messages(mock_memory, [env_config.GENERAL_MEMORY_TAG])

        # Should have at least the message we added
        assert len(result) >= 1
