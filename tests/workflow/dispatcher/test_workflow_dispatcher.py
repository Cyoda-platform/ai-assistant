import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from workflow.dispatcher.workflow_dispatcher import WorkflowDispatcher
from entity.model import AgenticFlowEntity, ChatMemory
from common.config.config import config as env_config
import common.config.const as const


class TestWorkflowDispatcher:
    """Test cases for WorkflowDispatcher."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for WorkflowDispatcher."""
        return {
            'cls': MagicMock(),
            'cls_instance': MagicMock(),
            'ai_agent': AsyncMock(),
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
            'user_service': AsyncMock(),
            'mock': False,
        }

    @pytest.fixture
    def dispatcher(self, mock_dependencies):
        """Create WorkflowDispatcher instance."""
        return WorkflowDispatcher(**mock_dependencies)

    @pytest.fixture
    def mock_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.technical_id = "test_tech_id"
        entity.workflow_cache = {}
        entity.failed = False
        entity.error = None
        return entity

    @pytest.fixture
    def mock_memory(self):
        """Create mock ChatMemory."""
        memory = MagicMock(spec=ChatMemory)
        memory.messages = {}
        memory.technical_id = "memory_tech_id"
        return memory

    @pytest.mark.asyncio
    async def test_dispatch_workflow_success(self, dispatcher, mock_entity, mock_memory):
        """Test successful workflow dispatching."""
        config = {
            "type": "ai_agent",
            "model": "gpt-4",
            "prompt": "Test prompt"
        }
        
        dispatcher.event_processor.process_event.return_value = "Event processed successfully"
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
        
        assert result == "Event processed successfully"
        dispatcher.event_processor.process_event.assert_called_once_with(
            config, mock_entity, mock_memory, "tech_id"
        )

    @pytest.mark.asyncio
    async def test_dispatch_workflow_error_handling(self, dispatcher, mock_entity, mock_memory):
        """Test workflow dispatching with error."""
        config = {"type": "ai_agent"}
        
        dispatcher.event_processor.process_event.side_effect = Exception("Processing error")
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
        
        assert "Error dispatching workflow" in result

    @pytest.mark.asyncio
    async def test_dispatch_workflow_with_memory_initialization(self, dispatcher, mock_entity):
        """Test workflow dispatching with memory initialization."""
        config = {"type": "notification", "notification": "Test message"}
        
        # Mock memory creation
        mock_new_memory = MagicMock(spec=ChatMemory)
        mock_new_memory.technical_id = "new_memory_id"
        dispatcher.entity_service.create_item.return_value = mock_new_memory
        
        dispatcher.event_processor.process_event.return_value = "Success"
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, None, "tech_id")
        
        assert result == "Success"
        # Should create new memory when none provided
        dispatcher.entity_service.create_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_workflow_preserves_existing_memory(self, dispatcher, mock_entity, mock_memory):
        """Test workflow dispatching preserves existing memory."""
        config = {"type": "question", "question": "Test question"}
        
        dispatcher.event_processor.process_event.return_value = "Question processed"
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
        
        assert result == "Question processed"
        # Should not create new memory when one is provided
        dispatcher.entity_service.create_item.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_workflow_with_complex_config(self, dispatcher, mock_entity, mock_memory):
        """Test workflow dispatching with complex configuration."""
        config = {
            "type": "ai_agent",
            "model": "gpt-4",
            "prompt": "Complex prompt with {variable}",
            "memory_tags": ["custom_tag"],
            "max_iterations": 5,
            "input": {
                "local_fs": ["file1.py", "file2.py"]
            },
            "output": {
                "edge_message": {
                    "message_type": "result",
                    "content_key": "response"
                }
            }
        }
        
        dispatcher.event_processor.process_event.return_value = "Complex workflow completed"
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
        
        assert result == "Complex workflow completed"
        dispatcher.event_processor.process_event.assert_called_once_with(
            config, mock_entity, mock_memory, "tech_id"
        )

    @pytest.mark.asyncio
    async def test_dispatch_workflow_updates_entity_state(self, dispatcher, mock_entity, mock_memory):
        """Test that workflow dispatching can update entity state."""
        config = {
            "type": "ai_agent",
            "output_variable": "result"
        }
        
        dispatcher.event_processor.process_event.return_value = "Workflow result"
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
        
        assert result == "Workflow result"
        # The event processor should handle updating the entity's workflow_cache

    @pytest.mark.asyncio
    async def test_dispatch_workflow_with_memory_tags(self, dispatcher, mock_entity, mock_memory):
        """Test workflow dispatching with specific memory tags."""
        config = {
            "type": "notification",
            "notification": "Tagged message",
            "memory_tags": ["tag1", "tag2"]
        }
        
        dispatcher.event_processor.process_event.return_value = "Tagged notification sent"
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
        
        assert result == "Tagged notification sent"

    @pytest.mark.asyncio
    async def test_dispatch_workflow_error_preserves_entity_state(self, dispatcher, mock_entity, mock_memory):
        """Test that errors don't corrupt entity state."""
        config = {"type": "ai_agent"}
        original_cache = mock_entity.workflow_cache.copy()
        
        dispatcher.event_processor.process_event.side_effect = Exception("Processing error")
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
        
        assert "Error dispatching workflow" in result
        # Entity state should be preserved
        assert mock_entity.workflow_cache == original_cache

    @pytest.mark.asyncio
    async def test_dispatch_workflow_with_iteration_tracking(self, dispatcher, mock_entity, mock_memory):
        """Test workflow dispatching with iteration tracking."""
        config = {
            "type": "ai_agent",
            "max_iterations": 3
        }
        
        mock_entity.workflow_cache = {"iteration_count": 1}
        dispatcher.event_processor.process_event.return_value = "Iteration completed"
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
        
        assert result == "Iteration completed"

    @pytest.mark.asyncio
    async def test_dispatch_workflow_memory_creation_error(self, dispatcher, mock_entity):
        """Test workflow dispatching when memory creation fails."""
        config = {"type": "ai_agent"}
        
        dispatcher.entity_service.create_item.side_effect = Exception("Memory creation failed")
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, None, "tech_id")
        
        assert "Error dispatching workflow" in result

    @pytest.mark.asyncio
    async def test_dispatch_workflow_with_empty_config(self, dispatcher, mock_entity, mock_memory):
        """Test workflow dispatching with empty configuration."""
        config = {}
        
        dispatcher.event_processor.process_event.return_value = "Empty config handled"
        
        result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
        
        assert result == "Empty config handled"

    @pytest.mark.asyncio
    async def test_dispatch_workflow_concurrent_execution(self, dispatcher, mock_entity, mock_memory):
        """Test workflow dispatching handles concurrent execution."""
        config1 = {"type": "notification", "notification": "Message 1"}
        config2 = {"type": "notification", "notification": "Message 2"}
        
        dispatcher.event_processor.process_event.side_effect = ["Result 1", "Result 2"]
        
        # Simulate concurrent dispatching
        import asyncio
        results = await asyncio.gather(
            dispatcher.dispatch_workflow(config1, mock_entity, mock_memory, "tech_id_1"),
            dispatcher.dispatch_workflow(config2, mock_entity, mock_memory, "tech_id_2")
        )
        
        assert results[0] == "Result 1"
        assert results[1] == "Result 2"

    def test_dispatcher_initialization(self, mock_dependencies):
        """Test WorkflowDispatcher initialization."""
        dispatcher = WorkflowDispatcher(**mock_dependencies)

        assert dispatcher.entity_service == mock_dependencies['entity_service']
        assert dispatcher.cyoda_auth_service == mock_dependencies['cyoda_auth_service']
        assert dispatcher.user_service == mock_dependencies['user_service']
        assert dispatcher.cls == mock_dependencies['cls']
        assert dispatcher.cls_instance == mock_dependencies['cls_instance']
        assert dispatcher.mock == mock_dependencies['mock']
        assert hasattr(dispatcher, 'method_registry')
        assert hasattr(dispatcher, 'memory_manager')
        assert hasattr(dispatcher, 'ai_agent_handler')
        assert hasattr(dispatcher, 'file_handler')
        assert hasattr(dispatcher, 'message_processor')
        assert hasattr(dispatcher, 'event_processor')
        assert hasattr(dispatcher, 'methods_dict')

    @pytest.mark.asyncio
    async def test_dispatch_workflow_logging(self, dispatcher, mock_entity, mock_memory):
        """Test that workflow dispatching includes proper logging."""
        config = {"type": "ai_agent", "model": "gpt-4"}
        
        dispatcher.event_processor.process_event.return_value = "Success"
        
        with patch.object(dispatcher.logger, 'info') as mock_log_info, \
             patch.object(dispatcher.logger, 'exception') as mock_log_exception:
            
            result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
            
            assert result == "Success"
            # Should log the workflow dispatch
            mock_log_info.assert_called()
            mock_log_exception.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_workflow_error_logging(self, dispatcher, mock_entity, mock_memory):
        """Test that workflow dispatching errors are properly logged."""
        config = {"type": "ai_agent"}
        
        dispatcher.event_processor.process_event.side_effect = Exception("Test error")
        
        with patch.object(dispatcher.logger, 'exception') as mock_log_exception:
            result = await dispatcher.dispatch_workflow(config, mock_entity, mock_memory, "tech_id")
            
            assert "Error dispatching workflow" in result
            mock_log_exception.assert_called_once()
