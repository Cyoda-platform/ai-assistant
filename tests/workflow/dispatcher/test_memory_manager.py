import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from workflow.dispatcher.memory_manager import MemoryManager
from entity.model import AgenticFlowEntity, ChatMemory, AIMessage, AIMemoryEdgeMessage
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
        
        mock_edge_message = MagicMock()
        mock_edge_message.technical_id = "edge_msg_123"
        manager.entity_service.create_item.return_value = mock_edge_message
        
        mock_ai_memory = MagicMock()
        mock_ai_memory.technical_id = "ai_memory_123"
        manager.entity_service.create_item.return_value = mock_ai_memory
        
        await manager.append_to_ai_memory(mock_entity, content, memory_tags)
        
        # Should create edge message and AI memory
        assert manager.entity_service.create_item.call_count >= 1

    @pytest.mark.asyncio
    async def test_append_to_ai_memory_with_single_tag(self, manager, mock_entity, mock_memory):
        """Test AI memory appending with single memory tag."""
        content = "Test content"
        memory_tags = [env_config.GENERAL_MEMORY_TAG]
        
        mock_edge_message = MagicMock()
        mock_edge_message.technical_id = "edge_msg_123"
        
        mock_ai_memory = MagicMock()
        mock_ai_memory.technical_id = "ai_memory_123"
        
        manager.entity_service.create_item.side_effect = [mock_edge_message, mock_ai_memory]
        
        await manager.append_to_ai_memory(mock_entity, content, memory_tags)
        
        # Verify edge message creation
        edge_message_call = manager.entity_service.create_item.call_args_list[0]
        assert edge_message_call[1]['entity_model'] == const.ModelName.EDGE_MESSAGE_STORE.value
        
        # Verify AI memory creation
        ai_memory_call = manager.entity_service.create_item.call_args_list[1]
        assert ai_memory_call[1]['entity_model'] == const.ModelName.AI_MEMORY_EDGE_MESSAGE.value

    @pytest.mark.asyncio
    async def test_append_to_ai_memory_multiple_tags(self, manager, mock_entity, mock_memory):
        """Test AI memory appending with multiple memory tags."""
        content = "Test content"
        memory_tags = ["tag1", "tag2", "tag3"]
        
        mock_edge_message = MagicMock()
        mock_edge_message.technical_id = "edge_msg_123"
        
        mock_ai_memory = MagicMock()
        mock_ai_memory.technical_id = "ai_memory_123"
        
        manager.entity_service.create_item.side_effect = [mock_edge_message] + [mock_ai_memory] * 3
        
        await manager.append_to_ai_memory(mock_entity, content, memory_tags)
        
        # Should create one edge message and three AI memory entries
        assert manager.entity_service.create_item.call_count == 4

    @pytest.mark.asyncio
    async def test_append_to_ai_memory_error_handling(self, manager, mock_entity, mock_memory):
        """Test AI memory appending with error."""
        content = "Test content"
        memory_tags = [env_config.GENERAL_MEMORY_TAG]
        
        manager.entity_service.create_item.side_effect = Exception("Create error")
        
        # Should not raise exception
        await manager.append_to_ai_memory(mock_entity, content, memory_tags)

    @pytest.mark.asyncio
    async def test_get_ai_memory_messages_success(self, manager, mock_memory):
        """Test successful AI memory messages retrieval."""
        memory_tags = [env_config.GENERAL_MEMORY_TAG, "custom_tag"]
        
        mock_ai_message1 = MagicMock()
        mock_ai_message1.edge_message_id = "edge_1"
        mock_ai_message2 = MagicMock()
        mock_ai_message2.edge_message_id = "edge_2"
        
        mock_memory.messages = {
            env_config.GENERAL_MEMORY_TAG: [mock_ai_message1],
            "custom_tag": [mock_ai_message2]
        }
        
        mock_message_content1 = AIMessage(role="user", content="Message 1")
        mock_message_content2 = AIMessage(role="user", content="Message 2")
        
        manager.entity_service.get_item.side_effect = [mock_message_content1, mock_message_content2]
        
        result = await manager.get_ai_memory_messages(mock_memory, memory_tags)
        
        assert len(result) == 2
        assert result[0] == mock_message_content1
        assert result[1] == mock_message_content2

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
        
        mock_ai_message = MagicMock()
        mock_ai_message.edge_message_id = "edge_1"
        mock_memory.messages = {env_config.GENERAL_MEMORY_TAG: [mock_ai_message]}
        
        manager.entity_service.get_item.side_effect = Exception("Get error")
        
        result = await manager.get_ai_memory_messages(mock_memory, memory_tags)
        
        # Should handle error gracefully and return empty list
        assert result == []

    @pytest.mark.asyncio
    async def test_append_to_ai_memory_with_timestamp(self, manager, mock_entity, mock_memory):
        """Test AI memory appending includes timestamp."""
        content = "Test content with timestamp"
        memory_tags = [env_config.GENERAL_MEMORY_TAG]
        
        mock_edge_message = MagicMock()
        mock_edge_message.technical_id = "edge_msg_123"
        
        mock_ai_memory = MagicMock()
        mock_ai_memory.technical_id = "ai_memory_123"
        
        manager.entity_service.create_item.side_effect = [mock_edge_message, mock_ai_memory]
        
        with patch('common.utils.utils.get_current_timestamp_num', return_value=1234567890):
            await manager.append_to_ai_memory(mock_entity, content, memory_tags)
            
            # Verify timestamp is included in edge message creation
            edge_message_call = manager.entity_service.create_item.call_args_list[0]
            edge_message_data = edge_message_call[1]['entity_data']
            assert edge_message_data.timestamp == 1234567890

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
        
        await manager.append_to_ai_memory(mock_entity, content, memory_tags, role=role)
        
        # Verify role is set correctly in edge message
        edge_message_call = manager.entity_service.create_item.call_args_list[0]
        edge_message_data = edge_message_call[1]['entity_data']
        assert edge_message_data.role == "assistant"

    @pytest.mark.asyncio
    async def test_memory_manager_integration(self, manager, mock_entity, mock_memory):
        """Test full integration of memory manager operations."""
        # First append some messages
        await manager.append_to_ai_memory(mock_entity, "Message 1", [env_config.GENERAL_MEMORY_TAG])
        await manager.append_to_ai_memory(mock_entity, "Message 2", [env_config.GENERAL_MEMORY_TAG])
        
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
        
        # Retrieve messages
        result = await manager.get_ai_memory_messages(mock_memory, [env_config.GENERAL_MEMORY_TAG])
        
        assert len(result) == 2
        assert result[0].content == "Message 1"
        assert result[1].content == "Message 2"
