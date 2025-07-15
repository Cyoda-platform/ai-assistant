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
            'method_registry': MagicMock(),
            'ai_agent_handler': AsyncMock(),
            'memory_manager': AsyncMock(),
            'file_handler': AsyncMock(),
            'message_processor': AsyncMock(),
            'user_service': AsyncMock(),
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
        }

    @pytest.fixture
    def processor(self, mock_dependencies):
        """Create EventProcessor instance."""
        return EventProcessor(**mock_dependencies)

    @pytest.fixture
    def mock_entity(self):
        """Create mock AgenticFlowEntity."""
        from entity.model import ChatFlow

        entity = MagicMock(spec=AgenticFlowEntity)
        entity.technical_id = "test_tech_id"
        entity.memory_id = "test_memory_id"
        entity.user_id = "test_user_id"
        entity.workflow_name = "test_workflow"
        entity.workflow_cache = {"test_key": "test_value", "name": "John", "user_id": "123"}
        entity.edge_messages_store = {}
        entity.failed = False
        entity.error = None
        entity.current_transition = "test_transition"
        entity.chat_flow = ChatFlow(current_flow=[], finished_flow=[])
        entity.child_entities = []
        entity.last_modified = 1234567890

        # Mock model_dump to return valid data for AgenticFlowEntity creation
        entity.model_dump.return_value = {
            "technical_id": "test_tech_id",
            "memory_id": "test_memory_id",
            "user_id": "test_user_id",
            "workflow_name": "test_workflow",
            "workflow_cache": {"test_key": "test_value", "name": "John", "user_id": "123"},
            "edge_messages_store": {},
            "failed": False,
            "error": None,
            "current_transition": "test_transition",
            "chat_flow": {"current_flow": [], "finished_flow": []},
            "child_entities": [],
            "last_modified": 1234567890,
            "transitions_memory": {"current_iteration": {}, "max_iteration": {}},
            "current_state": None,
            "error_code": "None"
        }

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
            "type": "agent",
            "model": {"model_name": "gpt-4o-mini"},
            "prompt": "Test prompt"
        }
        
        processor.ai_agent_handler.run_ai_agent = AsyncMock(return_value="AI response")
        processor.entity_service.add_item = AsyncMock(return_value="edge_msg_123")

        action = {"config": config}
        entity, result = await processor.process_event(mock_entity, action, "tech_id")

        assert result == "AI response"

    @pytest.mark.asyncio
    async def test_process_event_notification_success(self, processor, mock_entity, mock_memory):
        """Test successful notification event processing."""
        config = {
            "type": "notification",
            "notification": "Hello {test_key}!",
            "memory_tags": ["general"]
        }
        
        processor.entity_service.add_item = AsyncMock(return_value="edge_msg_123")

        action = {"config": config}
        with patch.object(processor, '_format_message', return_value="Hello test_value!"):
            entity, result = await processor.process_event(mock_entity, action, "tech_id")

            assert result == "Hello test_value!"

    @pytest.mark.asyncio
    async def test_process_event_question_success(self, processor, mock_entity, mock_memory):
        """Test successful question event processing."""
        config = {
            "type": "question",
            "question": "What is {test_key}?",
            "memory_tags": ["general"]
        }
        
        processor.entity_service.add_item = AsyncMock(return_value="edge_msg_123")

        action = {"config": config}
        with patch.object(processor, '_format_message', return_value="What is test_value?"):
            entity, result = await processor.process_event(mock_entity, action, "tech_id")

            assert result == "What is test_value?"

    @pytest.mark.asyncio
    async def test_process_event_unknown_type(self, processor, mock_entity, mock_memory):
        """Test processing event with unknown type."""
        config = {"type": "unknown_type"}
        
        processor.entity_service.add_item = AsyncMock(return_value="edge_msg_123")

        action = {"config": config}
        entity, result = await processor.process_event(mock_entity, action, "tech_id")

        assert "Unknown config type: unknown_type" in result

    @pytest.mark.asyncio
    async def test_process_event_error_handling(self, processor, mock_entity, mock_memory):
        """Test error handling in event processing."""
        config = {"type": "agent"}
        processor.ai_agent_handler.run_ai_agent.side_effect = Exception("AI error")
        
        action = {"config": config}
        entity, result = await processor.process_event(mock_entity, action, "tech_id")

        assert "Error:" in result

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
        config = {"type": "agent", "output_variable": "result_var"}
        response = "Test response"
        finished_flow = []
        new_entities = []

        with patch.object(processor, 'add_edge_message', new_callable=AsyncMock), \
             patch.object(processor, '_write_to_output', new_callable=AsyncMock):

            result = await processor._finalize_response(
                technical_id="tech_id",
                entity=mock_entity,
                config=config,
                finished_flow=finished_flow,
                response=response,
                new_entities=new_entities
            )

            assert result is None  # Method doesn't return anything

    @pytest.mark.asyncio
    async def test_finalize_response_no_output_variable(self, processor, mock_entity):
        """Test response finalization without output variable."""
        config = {"type": "notification"}
        response = "Test response"
        finished_flow = []
        new_entities = []

        with patch.object(processor, 'add_edge_message', new_callable=AsyncMock):
            result = await processor._finalize_response(
                technical_id="tech_id",
                entity=mock_entity,
                config=config,
                finished_flow=finished_flow,
                response=response,
                new_entities=new_entities
            )

            assert result is None  # Method doesn't return anything

    @pytest.mark.asyncio
    async def test_write_to_output_with_edge_message(self, processor, mock_entity):
        """Test writing to output with edge message creation."""
        config = {
            "output": {
                "cyoda_edge_message": ["test_edge"]
            }
        }
        response = "Test response"
        
        processor.entity_service.add_item = AsyncMock(return_value="edge_msg_123")
        
        result = await processor._write_to_output(mock_entity, config, response, "tech_id")
        
        assert result is None  # Method doesn't return anything
        processor.entity_service.add_item.assert_called_once()
        # Check that edge message ID is stored in entity
        assert mock_entity.edge_messages_store["test_edge"] == "edge_msg_123"

    @pytest.mark.asyncio
    async def test_write_to_output_with_local_fs(self, processor, mock_entity):
        """Test writing to output with local filesystem."""
        config = {
            "output": {
                "local_fs": ["output.txt"]
            }
        }
        response = "Test response"
        
        with patch.object(processor, '_save_file', new_callable=AsyncMock) as mock_save, \
             patch.object(processor, '_get_repository_name', return_value="test_repo"):

            result = await processor._write_to_output(mock_entity, config, response, "tech_id")

            assert result is None  # Method doesn't return anything
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_to_output_no_output_config(self, processor, mock_entity):
        """Test writing to output with no output configuration."""
        config = {}
        response = "Test response"
        
        result = await processor._write_to_output(mock_entity, config, response, "tech_id")

        assert result is None  # Method doesn't return anything

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
        
        result = await processor._write_to_output(mock_entity, config, response, "tech_id")

        assert result is None  # Method doesn't return anything

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
        
        # Should return original message when formatting fails
        assert result == message
