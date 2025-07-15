import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from workflow.dispatcher.ai_agent_handler import AIAgentHandler
from workflow.dispatcher.method_registry import MethodRegistry
from workflow.dispatcher.memory_manager import MemoryManager
from entity.model import AgenticFlowEntity, ChatMemory, AIMessage, ModelConfig, TransitionsMemory
from common.config.config import config as env_config
import common.config.const as const


class TestAIAgentHandler:
    """Test cases for AIAgentHandler."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for AIAgentHandler."""
        # Create mock workflow class and instance
        class MockWorkflowClass:
            def __init__(self):
                self._function_registry = {
                    'test_function': AsyncMock(return_value="test_result")
                }

        mock_instance = MockWorkflowClass()

        return {
            'ai_agent': AsyncMock(),
            'method_registry': MethodRegistry(MockWorkflowClass, mock_instance),
            'memory_manager': MagicMock(spec=MemoryManager),
            'cls_instance': mock_instance,
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
        }

    @pytest.fixture
    def handler(self, mock_dependencies):
        """Create AIAgentHandler instance."""
        return AIAgentHandler(**mock_dependencies)

    @pytest.fixture
    def mock_entity(self):
        """Create mock AgenticFlowEntity."""
        from entity.model import ChatFlow

        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {
            const.GIT_BRANCH_PARAM: "test_branch",
            "iteration_count": 0
        }
        entity.technical_id = "test_tech_id"
        entity.memory_id = "test_memory_id"
        entity.user_id = "test_user_id"
        entity.edge_messages_store = {}
        entity.current_transition = "test_transition"
        entity.chat_flow = ChatFlow(current_flow=[], finished_flow=[])
        entity.transitions_memory = TransitionsMemory(
            current_iteration={},
            max_iteration={}
        )
        return entity

    @pytest.fixture
    def mock_memory(self):
        """Create mock ChatMemory."""
        memory = MagicMock(spec=ChatMemory)
        memory.messages = {
            env_config.GENERAL_MEMORY_TAG: []
        }
        return memory

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        return {
            "model": {"model_name": "gpt-4o-mini"},
            "prompt": "Test prompt",
            "memory_tags": [env_config.GENERAL_MEMORY_TAG],
            "max_iterations": 3
        }

    @pytest.mark.asyncio
    async def test_run_ai_agent_success(self, handler, mock_entity, mock_memory, mock_config):
        """Test successful AI agent execution."""
        mock_messages = [AIMessage(role="user", content="Test message")]
        
        # Mock the AI agent to return a response
        handler.ai_agent.run_agent = AsyncMock(return_value="AI response")

        with patch.object(handler, '_get_ai_memory', return_value=mock_messages), \
             patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch.object(handler, '_append_messages', new_callable=AsyncMock):

            result = await handler.run_ai_agent(mock_config, mock_entity, mock_memory, "tech_id")

            assert result == "AI response"

    @pytest.mark.asyncio
    async def test_run_ai_agent_max_iterations_exceeded(self, handler, mock_entity, mock_memory, mock_config):
        """Test AI agent execution with max iterations exceeded."""
        mock_entity.workflow_cache["iteration_count"] = 5
        mock_config["max_iteration"] = 3

        with patch.object(handler, '_check_and_update_iteration', return_value=True):
            result = await handler.run_ai_agent(mock_config, mock_entity, mock_memory, "tech_id")

            assert "Let's proceed to the next iteration" in result

    @pytest.mark.asyncio
    async def test_run_ai_agent_error_handling(self, handler, mock_entity, mock_memory, mock_config):
        """Test AI agent execution with error."""
        with patch.object(handler, '_get_ai_memory', side_effect=Exception("Memory error")):
            result = await handler.run_ai_agent(mock_config, mock_entity, mock_memory, "tech_id")
            
            assert "Error running AI agent" in result

    @pytest.mark.asyncio
    async def test_get_ai_memory_basic(self, handler, mock_entity, mock_memory):
        """Test basic AI memory retrieval."""
        config = {"memory_tags": [env_config.GENERAL_MEMORY_TAG]}
        
        mock_ai_message = MagicMock()
        mock_ai_message.edge_message_id = "msg_123"
        mock_memory.messages[env_config.GENERAL_MEMORY_TAG] = [mock_ai_message]
        
        mock_message_content = AIMessage(role="user", content="Test content")
        handler.entity_service.get_item.return_value = mock_message_content
        
        result = await handler._get_ai_memory(mock_entity, config, mock_memory, "tech_id")
        
        assert len(result) == 1
        assert result[0] == mock_message_content

    @pytest.mark.asyncio
    async def test_get_ai_memory_with_local_fs_input(self, handler, mock_entity, mock_memory):
        """Test AI memory retrieval with local filesystem input."""
        config = {
            "memory_tags": [env_config.GENERAL_MEMORY_TAG],
            "input": {
                "local_fs": ["test_file.py"]
            }
        }
        
        with patch.object(handler, '_read_local_file', return_value="file content"), \
             patch.object(handler, '_get_repository_name', return_value="test_repo"):
            
            result = await handler._get_ai_memory(mock_entity, config, mock_memory, "tech_id")
            
            # Should include file content as a message
            assert any("Reference: test_file.py" in str(msg.content) for msg in result)

    @pytest.mark.asyncio
    async def test_get_ai_memory_with_cyoda_edge_message_input(self, handler, mock_entity, mock_memory):
        """Test AI memory retrieval with Cyoda edge message input."""
        config = {
            "memory_tags": [env_config.GENERAL_MEMORY_TAG],
            "input": {
                "cyoda_edge_message": ["edge_msg_1"]
            }
        }
        
        mock_entity.edge_messages_store = {"edge_msg_1": "stored_msg_123"}
        mock_message_content = "Edge message content"
        handler.entity_service.get_item.return_value = mock_message_content
        
        result = await handler._get_ai_memory(mock_entity, config, mock_memory, "tech_id")
        
        # Should include edge message content
        assert any("Reference:" in str(msg.content) for msg in result)

    @pytest.mark.asyncio
    async def test_get_ai_memory_with_formatted_filename(self, handler, mock_entity, mock_memory):
        """Test AI memory retrieval with formatted filename."""
        config = {
            "memory_tags": [env_config.GENERAL_MEMORY_TAG],
            "input": {
                "local_fs": ["{entity_name}_model.py"]
            }
        }
        
        mock_entity.workflow_cache = {
            const.GIT_BRANCH_PARAM: "test_branch",
            "entity_name": "User"
        }
        
        with patch.object(handler, '_read_local_file', return_value="model content") as mock_read, \
             patch.object(handler, '_get_repository_name', return_value="test_repo"):
            
            result = await handler._get_ai_memory(mock_entity, config, mock_memory, "tech_id")
            
            mock_read.assert_called_once_with(
                file_name="User_model.py",
                technical_id="test_branch",
                branch_name_id="test_branch",
                repository_name="test_repo"
            )

    @pytest.mark.asyncio
    async def test_read_local_file_success(self, handler):
        """Test successful local file reading."""
        with patch('common.utils.utils.get_project_file_name_path', 
                   new_callable=AsyncMock, return_value="/path/to/file.py"), \
             patch('aiofiles.open', create=True) as mock_open:
            
            mock_file = AsyncMock()
            mock_file.read.return_value = "file content"
            mock_open.return_value.__aenter__.return_value = mock_file
            
            result = await handler._read_local_file("test.py", "tech_id", "branch", "repo")
            
            assert result == "file content"

    @pytest.mark.asyncio
    async def test_read_local_file_error(self, handler):
        """Test local file reading with error."""
        with patch('common.utils.utils.get_project_file_name_path', 
                   new_callable=AsyncMock, side_effect=Exception("File error")):
            
            result = await handler._read_local_file("test.py", "tech_id", "branch", "repo")
            
            assert result == ""

    def test_get_repository_name(self, handler):
        """Test repository name retrieval."""
        mock_entity = MagicMock()
        
        with patch('common.utils.utils.get_repository_name', return_value="test_repo") as mock_get_repo:
            result = handler._get_repository_name(mock_entity)
            
            assert result == "test_repo"
            mock_get_repo.assert_called_once_with(mock_entity)

    def test_check_and_update_iteration_within_limit(self, handler, mock_entity):
        """Test iteration check when within limit."""
        mock_entity.current_transition = "test_transition"
        mock_entity.transitions_memory.current_iteration = {"test_transition": 2}
        mock_entity.transitions_memory.max_iteration = {}
        config = {"max_iteration": 5}

        result = handler._check_and_update_iteration(config, mock_entity)

        assert result is False  # Should return False when within limit
        assert mock_entity.transitions_memory.current_iteration["test_transition"] == 3

    def test_check_and_update_iteration_exceeds_limit(self, handler, mock_entity):
        """Test iteration check when exceeding limit."""
        mock_entity.current_transition = "test_transition"
        mock_entity.transitions_memory.current_iteration = {"test_transition": 5}
        mock_entity.transitions_memory.max_iteration = {"test_transition": 3}
        config = {"max_iteration": 3}

        result = handler._check_and_update_iteration(config, mock_entity)

        assert result is True  # Should return True when exceeding limit
        # The method doesn't increment when exceeding limit, it just returns True
        assert mock_entity.transitions_memory.current_iteration["test_transition"] == 5

    def test_check_and_update_iteration_no_limit(self, handler, mock_entity):
        """Test iteration check with no max_iteration specified."""
        mock_entity.current_transition = "test_transition"
        mock_entity.transitions_memory.current_iteration = {}
        mock_entity.transitions_memory.max_iteration = {}
        config = {}

        result = handler._check_and_update_iteration(config, mock_entity)

        assert result is False  # Should return False when no limit specified

    def test_check_and_update_iteration_first_iteration(self, handler, mock_entity):
        """Test iteration check for first iteration."""
        mock_entity.current_transition = "test_transition"
        mock_entity.transitions_memory.current_iteration = {}
        mock_entity.transitions_memory.max_iteration = {}
        config = {"max_iteration": 3}

        result = handler._check_and_update_iteration(config, mock_entity)

        assert result is False  # Should return False for first iteration
        assert mock_entity.transitions_memory.current_iteration["test_transition"] == 1
        assert mock_entity.transitions_memory.max_iteration["test_transition"] == 3

    @pytest.mark.asyncio
    async def test_append_messages_success(self, handler, mock_entity, mock_memory):
        """Test successful message appending."""
        config = {
            "messages": [AIMessage(role="user", content="Test message")],
            "memory_tags": [env_config.GENERAL_MEMORY_TAG]
        }
        finished_flow = []

        handler.entity_service.add_item = AsyncMock(return_value="edge_msg_123")

        with patch('common.utils.chat_util_functions.enrich_config_message', new_callable=AsyncMock, return_value=AIMessage(role="user", content="Test message")):
            result = await handler._append_messages(mock_entity, config, mock_memory, finished_flow)

            assert result is None  # Method doesn't return anything

    @pytest.mark.asyncio
    async def test_append_messages_error(self, handler, mock_entity, mock_memory):
        """Test message appending with error."""
        config = {
            "messages": [AIMessage(role="user", content="Test")],
            "memory_tags": [env_config.GENERAL_MEMORY_TAG]
        }
        finished_flow = []

        handler.entity_service.add_item = AsyncMock(side_effect=Exception("Append error"))

        with patch('common.utils.chat_util_functions.enrich_config_message', new_callable=AsyncMock, return_value=AIMessage(role="user", content="Test")):
            # Should raise exception since error handling is not implemented in this method
            with pytest.raises(Exception, match="Append error"):
                await handler._append_messages(mock_entity, config, mock_memory, finished_flow)
