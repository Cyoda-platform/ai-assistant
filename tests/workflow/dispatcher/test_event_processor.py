import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from workflow.dispatcher.event_processor import EventProcessor
from entity.model import AgenticFlowEntity, ChatMemory, FlowEdgeMessage
from common.config.config import config as env_config
import common.config.const as const


class TestEventProcessor:
    """Test cases for EventProcessor."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for EventProcessor."""
        return {
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
            'ai_agent_handler': AsyncMock(),
            'memory_manager': AsyncMock(),
        }

    @pytest.fixture
    def processor(self, mock_dependencies):
        """Create EventProcessor instance."""
        return EventProcessor(**mock_dependencies)

    @pytest.fixture
    def mock_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {"test_key": "test_value"}
        entity.technical_id = "test_tech_id"
        entity.failed = False
        entity.error = None
        return entity

    @pytest.fixture
    def mock_memory(self):
        """Create mock ChatMemory."""
        memory = MagicMock(spec=ChatMemory)
        memory.messages = {}
        return memory

    @pytest.mark.asyncio
    async def test_process_event_ai_agent_success(self, processor, mock_entity, mock_memory):
        """Test successful AI agent event processing."""
        config = {
            "type": "ai_agent",
            "model": "gpt-4",
            "prompt": "Test prompt"
        }
        
        processor.ai_agent_handler.run_ai_agent.return_value = "AI response"
        
        result = await processor.process_event(config, mock_entity, mock_memory, "tech_id")
        
        assert result == "AI response"
        processor.ai_agent_handler.run_ai_agent.assert_called_once_with(
            config=config, entity=mock_entity, memory=mock_memory, technical_id="tech_id"
        )

    @pytest.mark.asyncio
    async def test_process_event_notification_success(self, processor, mock_entity, mock_memory):
        """Test successful notification event processing."""
        config = {
            "type": "notification",
            "notification": "Hello {test_key}!",
            "memory_tags": ["general"]
        }
        
        with patch.object(processor, '_format_message', return_value="Hello test_value!"):
            result = await processor.process_event(config, mock_entity, mock_memory, "tech_id")
            
            assert result == "Hello test_value!"
            # Check that config was updated with formatted message
            assert config["notification"] == "Hello test_value!"
            processor.memory_manager.append_to_ai_memory.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_event_question_success(self, processor, mock_entity, mock_memory):
        """Test successful question event processing."""
        config = {
            "type": "question",
            "question": "What is {test_key}?",
            "memory_tags": ["general"]
        }
        
        with patch.object(processor, '_format_message', return_value="What is test_value?"):
            result = await processor.process_event(config, mock_entity, mock_memory, "tech_id")
            
            assert result == "What is test_value?"
            # Check that config was updated with formatted message
            assert config["question"] == "What is test_value?"
            processor.memory_manager.append_to_ai_memory.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_event_unknown_type(self, processor, mock_entity, mock_memory):
        """Test processing event with unknown type."""
        config = {"type": "unknown_type"}
        
        result = await processor.process_event(config, mock_entity, mock_memory, "tech_id")
        
        assert result == "Unknown event type: unknown_type"

    @pytest.mark.asyncio
    async def test_process_event_error_handling(self, processor, mock_entity, mock_memory):
        """Test error handling in event processing."""
        config = {"type": "ai_agent"}
        processor.ai_agent_handler.run_ai_agent.side_effect = Exception("AI error")
        
        result = await processor.process_event(config, mock_entity, mock_memory, "tech_id")
        
        assert "Error processing event" in result

    @pytest.mark.asyncio
    async def test_handle_notification_or_question_with_memory(self, processor, mock_entity):
        """Test notification/question handling with memory storage."""
        config = {
            "type": "notification",
            "notification": "Test message",
            "memory_tags": ["custom_tag"]
        }
        
        with patch.object(processor, '_format_message', return_value="Formatted message"):
            result = await processor._handle_notification_or_question(config, mock_entity)
            
            assert result == "Formatted message"
            assert config["notification"] == "Formatted message"
            processor.memory_manager.append_to_ai_memory.assert_called_once_with(
                entity=mock_entity,
                content="Formatted message",
                memory_tags=["custom_tag"]
            )

    @pytest.mark.asyncio
    async def test_handle_notification_or_question_default_memory_tag(self, processor, mock_entity):
        """Test notification/question handling with default memory tag."""
        config = {
            "type": "question",
            "question": "Test question"
        }
        
        with patch.object(processor, '_format_message', return_value="Formatted question"):
            result = await processor._handle_notification_or_question(config, mock_entity)
            
            assert result == "Formatted question"
            processor.memory_manager.append_to_ai_memory.assert_called_once_with(
                entity=mock_entity,
                content="Formatted question",
                memory_tags=[env_config.GENERAL_MEMORY_TAG]
            )

    @pytest.mark.asyncio
    async def test_finalize_response_success(self, processor, mock_entity):
        """Test successful response finalization."""
        config = {"output_variable": "result_var"}
        response = "Test response"
        
        result = await processor._finalize_response(config, mock_entity, response, "tech_id")
        
        assert result == response
        assert mock_entity.workflow_cache["result_var"] == response

    @pytest.mark.asyncio
    async def test_finalize_response_no_output_variable(self, processor, mock_entity):
        """Test response finalization without output variable."""
        config = {}
        response = "Test response"
        
        result = await processor._finalize_response(config, mock_entity, response, "tech_id")
        
        assert result == response
        # Should not modify workflow_cache when no output_variable

    @pytest.mark.asyncio
    async def test_write_to_output_with_edge_message(self, processor, mock_entity):
        """Test writing to output with edge message creation."""
        config = {
            "output": {
                "edge_message": {
                    "message_type": "test_type",
                    "content_key": "test_content"
                }
            }
        }
        response = "Test response"
        
        mock_edge_message = MagicMock()
        mock_edge_message.technical_id = "edge_msg_123"
        processor.entity_service.create_item.return_value = mock_edge_message
        
        result = await processor._write_to_output(config, mock_entity, response, "tech_id")
        
        assert result == response
        processor.entity_service.create_item.assert_called_once()
        # Check that edge message ID is stored in entity
        assert hasattr(mock_entity, 'edge_messages_store')

    @pytest.mark.asyncio
    async def test_write_to_output_with_local_fs(self, processor, mock_entity):
        """Test writing to output with local filesystem."""
        config = {
            "output": {
                "local_fs": {
                    "filename": "output.txt",
                    "content": "file_content"
                }
            }
        }
        response = "Test response"
        
        with patch('common.utils.utils._save_file', new_callable=AsyncMock) as mock_save, \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):
            
            result = await processor._write_to_output(config, mock_entity, response, "tech_id")
            
            assert result == response
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_to_output_no_output_config(self, processor, mock_entity):
        """Test writing to output with no output configuration."""
        config = {}
        response = "Test response"
        
        result = await processor._write_to_output(config, mock_entity, response, "tech_id")
        
        assert result == response

    @pytest.mark.asyncio
    async def test_write_to_output_error_handling(self, processor, mock_entity):
        """Test error handling in output writing."""
        config = {
            "output": {
                "edge_message": {
                    "message_type": "test_type"
                }
            }
        }
        response = "Test response"
        
        processor.entity_service.create_item.side_effect = Exception("Create error")
        
        result = await processor._write_to_output(config, mock_entity, response, "tech_id")
        
        assert result == response  # Should still return response even if output fails

    def test_format_message(self, processor):
        """Test message formatting with cache substitution."""
        message = "Hello {name}, your ID is {user_id}"
        cache = {"name": "John", "user_id": "123"}
        
        result = processor._format_message(message, cache)
        
        assert result == "Hello John, your ID is 123"

    def test_format_message_missing_keys(self, processor):
        """Test message formatting with missing cache keys."""
        message = "Hello {name}, your ID is {user_id}"
        cache = {"name": "John"}  # Missing user_id
        
        result = processor._format_message(message, cache)
        
        # Should handle missing keys gracefully
        assert "Hello John" in result
