import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from workflow.dispatcher.workflow_dispatcher import WorkflowDispatcher
from workflow.dispatcher.method_registry import MethodRegistry
from workflow.dispatcher.memory_manager import MemoryManager
from entity.model import WorkflowEntity, AgenticFlowEntity, ChatMemory, AIMessage, FlowEdgeMessage, ChatFlow
from common.config.config import config as env_config
import common.config.const as const


class TestWorkflowDispatcher:
    """Test cases for the refactored WorkflowDispatcher."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for WorkflowDispatcher."""
        return {
            'ai_agent': AsyncMock(),
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
            'user_service': AsyncMock(),
        }

    @pytest.fixture
    def mock_workflow_class(self):
        """Create a mock workflow class."""
        class MockWorkflowClass:
            def __init__(self):
                self._function_registry = {
                    'test_function': AsyncMock(return_value="test_result"),
                    'error_function': AsyncMock(side_effect=Exception("test error"))
                }
            
            async def traditional_method(self, technical_id, entity):
                return f"traditional_result_{technical_id}"
        
        return MockWorkflowClass

    @pytest.fixture
    def mock_workflow_instance(self, mock_workflow_class):
        """Create a mock workflow instance."""
        return mock_workflow_class()

    @pytest.fixture
    def dispatcher(self, mock_workflow_class, mock_workflow_instance, mock_dependencies):
        """Create WorkflowDispatcher instance."""
        return WorkflowDispatcher(
            cls=mock_workflow_class,
            cls_instance=mock_workflow_instance,
            **mock_dependencies
        )

    @pytest.fixture
    def mock_entity(self):
        """Create mock WorkflowEntity."""
        entity = MagicMock(spec=WorkflowEntity)
        entity.technical_id = "test_tech_id"
        entity.memory_id = "test_memory_id"
        entity.user_id = "test_user_id"
        entity.workflow_cache = {}
        entity.edge_messages_store = {}
        entity.failed = False
        entity.error = None
        entity.current_transition = "test_transition"
        entity.chat_flow = ChatFlow(current_flow=[], finished_flow=[])
        return entity

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.technical_id = "test_tech_id"
        entity.memory_id = "test_memory_id"
        entity.user_id = "test_user_id"
        entity.workflow_cache = {}
        entity.edge_messages_store = {}
        entity.failed = False
        entity.error = None
        entity.current_transition = "test_transition"
        entity.chat_flow = ChatFlow(current_flow=[], finished_flow=[])
        entity.transitions_memory = MagicMock()
        entity.transitions_memory.current_iteration = {}
        entity.transitions_memory.max_iteration = {}
        return entity

    def test_dispatcher_initialization(self, dispatcher):
        """Test that WorkflowDispatcher initializes correctly."""
        assert dispatcher is not None
        assert isinstance(dispatcher.method_registry, MethodRegistry)
        assert isinstance(dispatcher.memory_manager, MemoryManager)
        assert dispatcher.methods_dict is not None

    def test_get_available_methods(self, dispatcher):
        """Test getting available methods."""
        methods = dispatcher.get_available_methods()
        assert isinstance(methods, list)
        assert len(methods) > 0
        # Should include both registry and traditional methods
        assert 'test_function' in methods
        assert 'traditional_method' in methods

    @pytest.mark.asyncio
    async def test_dispatch_function_success(self, dispatcher):
        """Test successful function dispatch."""
        result = await dispatcher.dispatch_function(
            'test_function',
            technical_id='test_id',
            entity=MagicMock()
        )
        assert result == "test_result"

    @pytest.mark.asyncio
    async def test_dispatch_function_error(self, dispatcher):
        """Test function dispatch with error."""
        result = await dispatcher.dispatch_function(
            'error_function',
            technical_id='test_id',
            entity=MagicMock()
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_dispatch_function_not_found(self, dispatcher):
        """Test function dispatch with non-existent function."""
        result = await dispatcher.dispatch_function(
            'nonexistent_function',
            technical_id='test_id'
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_process_event_success(self, dispatcher, mock_agentic_entity):
        """Test successful event processing."""
        action = {
            "name": "test_function",
            "config": {
                "type": "function",
                "function": {
                    "name": "test_function"
                }
            }
        }
        
        # Mock the event processor
        dispatcher.event_processor.process_event = AsyncMock(
            return_value=(mock_agentic_entity, "success_response")
        )
        
        entity, response = await dispatcher.process_event(
            entity=mock_agentic_entity,
            action=action,
            technical_id="test_tech_id"
        )
        
        assert entity == mock_agentic_entity
        assert response == "success_response"
        dispatcher.event_processor.process_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_event_error(self, dispatcher, mock_agentic_entity):
        """Test event processing with error."""
        action = {"name": "error_function"}
        
        # Mock the event processor to raise an exception
        dispatcher.event_processor.process_event = AsyncMock(
            side_effect=Exception("Processing error")
        )
        
        entity, response = await dispatcher.process_event(
            entity=mock_agentic_entity,
            action=action,
            technical_id="test_tech_id"
        )
        
        assert entity.failed is True
        assert "Dispatcher error" in entity.error
        assert "Error:" in response

    @pytest.mark.asyncio
    async def test_validate_configuration_function_valid(self, dispatcher):
        """Test config validation for valid function."""
        config = {
            "type": "function",
            "function": {
                "name": "test_function"
            }
        }
        
        is_valid, error_msg = await dispatcher.validate_configuration(config)
        assert is_valid is True
        assert error_msg == ""

    @pytest.mark.asyncio
    async def test_validate_configuration_function_invalid(self, dispatcher):
        """Test config validation for invalid function."""
        config = {
            "type": "function",
            "function": {
                "name": "nonexistent_function"
            }
        }
        
        is_valid, error_msg = await dispatcher.validate_configuration(config)
        assert is_valid is False
        assert "not found" in error_msg

    @pytest.mark.asyncio
    async def test_validate_configuration_function_missing_name(self, dispatcher):
        """Test config validation for function without name."""
        config = {
            "type": "function",
            "function": {}
        }
        
        is_valid, error_msg = await dispatcher.validate_configuration(config)
        assert is_valid is False
        assert "Function name is required" in error_msg

    @pytest.mark.asyncio
    async def test_validate_configuration_ai_agent(self, dispatcher):
        """Test config validation for AI agent."""
        config = {
            "type": "agent",
            "model": {"model_name": "gpt-4o-mini"},
            "messages": []
        }
        
        # Mock the AI agent handler validation
        dispatcher.ai_agent_handler.validate_config = MagicMock(return_value=(True, ""))
        
        is_valid, error_msg = await dispatcher.validate_configuration(config)
        assert is_valid is True
        assert error_msg == ""
        dispatcher.ai_agent_handler.validate_config.assert_called_once_with(config)

    def test_get_component_status(self, dispatcher):
        """Test getting component status."""
        status = dispatcher.get_component_status()
        
        assert isinstance(status, dict)
        assert "method_registry" in status
        assert "memory_manager" in status
        assert "ai_agent_handler" in status
        assert "file_handler" in status
        assert "message_processor" in status
        assert "event_processor" in status
        
        # Check method registry status
        assert status["method_registry"]["methods_count"] > 0
        assert status["method_registry"]["has_function_registry"] is True
        
        # Check other components are initialized
        for component in ["memory_manager", "ai_agent_handler", "file_handler", 
                         "message_processor", "event_processor"]:
            assert status[component]["initialized"] is True

    @pytest.mark.asyncio
    async def test_backward_compatibility_collect_methods(self, dispatcher):
        """Test backward compatibility method for collecting methods."""
        methods = await dispatcher._collect_subclass_methods()
        assert isinstance(methods, dict)
        assert len(methods) > 0

    @pytest.mark.asyncio
    async def test_backward_compatibility_execute_method(self, dispatcher, mock_entity):
        """Test backward compatibility method for executing methods."""
        result = await dispatcher._execute_method(
            method_name="test_function",
            technical_id="test_id",
            entity=mock_entity
        )
        assert result == "test_result"

    def test_mock_mode_initialization(self, mock_workflow_class, mock_workflow_instance, mock_dependencies):
        """Test WorkflowDispatcher initialization in mock mode."""
        dispatcher = WorkflowDispatcher(
            cls=mock_workflow_class,
            cls_instance=mock_workflow_instance,
            mock=True,
            **mock_dependencies
        )
        
        assert dispatcher.mock is True
        assert dispatcher is not None
