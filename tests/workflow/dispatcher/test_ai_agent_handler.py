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
        # Add attributes needed for save_all functionality
        entity.branch_id = "test_branch"
        entity.repository_name = "test_repo"
        entity.workflow_name = "java_template"
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

            assert "Sorry, i'm having a little trouble with the LLM" in result

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
        
        with patch.object(handler, '_read_local_path', return_value="file content"), \
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
    async def test_get_ai_memory_with_directory_input(self, handler, mock_entity, mock_memory):
        """Test AI memory retrieval with directory input."""
        config = {
            "memory_tags": [env_config.GENERAL_MEMORY_TAG],
            "input": {
                "local_fs": ["src/main/java/entities"]
            }
        }

        directory_content = """Directory: src/main/java/entities
==================================================
Found 2 files:

--- File: User.java ---
public class User {
    private String name;
}

--- File: Product.java ---
public class Product {
    private String title;
}
"""

        with patch.object(handler, '_read_local_path', return_value=directory_content), \
             patch.object(handler, '_get_repository_name', return_value="test_repo"):

            result = await handler._get_ai_memory(mock_entity, config, mock_memory, "tech_id")

            # Should include directory content as a message
            assert any("Reference: src/main/java/entities" in str(msg.content) for msg in result)
            assert any("Directory: src/main/java/entities" in str(msg.content) for msg in result)
            assert any("User.java" in str(msg.content) for msg in result)
            assert any("Product.java" in str(msg.content) for msg in result)

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
        
        with patch.object(handler, '_read_local_path', return_value="model content") as mock_read, \
             patch.object(handler, '_get_repository_name', return_value="test_repo"):

            result = await handler._get_ai_memory(mock_entity, config, mock_memory, "tech_id")

            mock_read.assert_called_once_with(
                path_name="User_model.py",
                technical_id="test_branch",
                branch_name_id="test_branch",
                repository_name="test_repo"
            )

    @pytest.mark.asyncio
    async def test_read_local_path_file_success(self, handler):
        """Test successful local file reading via _read_local_path."""
        with patch('common.utils.utils.get_project_file_name_path',
                   new_callable=AsyncMock, return_value="/path/to/file.py"), \
             patch.object(handler, '_path_exists', return_value=True), \
             patch.object(handler, '_is_directory', return_value=False), \
             patch.object(handler, '_read_local_file', return_value="file content"):

            result = await handler._read_local_path("test.py", "tech_id", "branch", "repo")

            assert result == "file content"

    @pytest.mark.asyncio
    async def test_read_local_path_directory_success(self, handler):
        """Test successful local directory reading via _read_local_path."""
        with patch('common.utils.utils.get_project_file_name_path',
                   new_callable=AsyncMock, return_value="/path/to/directory"), \
             patch.object(handler, '_path_exists', return_value=True), \
             patch.object(handler, '_is_directory', return_value=True), \
             patch.object(handler, '_read_local_directory', return_value="directory content"):

            result = await handler._read_local_path("test_dir", "tech_id", "branch", "repo")

            assert result == "directory content"

    @pytest.mark.asyncio
    async def test_read_local_path_not_found(self, handler):
        """Test local path reading when path doesn't exist."""
        with patch('common.utils.utils.get_project_file_name_path',
                   new_callable=AsyncMock, return_value="/path/to/nonexistent"), \
             patch.object(handler, '_path_exists', return_value=False):

            result = await handler._read_local_path("nonexistent", "tech_id", "branch", "repo")

            assert "Path not found: nonexistent" in result

    @pytest.mark.asyncio
    async def test_read_local_path_error(self, handler):
        """Test local path reading with error."""
        with patch('common.utils.utils.get_project_file_name_path',
                   new_callable=AsyncMock, side_effect=Exception("Path error")):

            result = await handler._read_local_path("test.py", "tech_id", "branch", "repo")

            assert "Error reading test.py" in result

    @pytest.mark.asyncio
    async def test_read_local_file_success(self, handler):
        """Test successful individual file reading."""
        with patch('aiofiles.open', create=True) as mock_open:
            mock_file = AsyncMock()
            mock_file.read.return_value = "file content"
            mock_open.return_value.__aenter__.return_value = mock_file

            result = await handler._read_local_file("/path/to/file.py", "file.py")

            assert result == "file content"

    @pytest.mark.asyncio
    async def test_read_local_file_error(self, handler):
        """Test individual file reading with error."""
        with patch('aiofiles.open', create=True, side_effect=Exception("File read error")):

            result = await handler._read_local_file("/path/to/file.py", "file.py")

            assert "Error reading file file.py" in result

    @pytest.mark.asyncio
    async def test_read_local_directory_success(self, handler):
        """Test successful directory reading with files."""
        mock_files = ["file1.py", "file2.java", "file3.txt"]

        with patch.object(handler, '_get_all_files_recursively', return_value=mock_files), \
             patch.object(handler, '_read_local_file', side_effect=["content1", "content2", "content3"]):

            result = await handler._read_local_directory("/path/to/directory", "test_dir")

            assert "Directory: test_dir" in result
            assert "Found 3 files (including subdirectories):" in result
            assert "--- File: file1.py ---" in result
            assert "--- File: file2.java ---" in result
            assert "--- File: file3.txt ---" in result
            assert "content1" in result
            assert "content2" in result
            assert "content3" in result

    @pytest.mark.asyncio
    async def test_read_local_directory_empty(self, handler):
        """Test directory reading when directory is empty."""
        with patch.object(handler, '_list_files_in_directory', return_value=[]):

            result = await handler._read_local_directory("/path/to/empty", "empty_dir")

            assert "Directory: empty_dir" in result
            assert "Directory is empty or contains no readable files." in result

    @pytest.mark.asyncio
    async def test_read_local_directory_with_file_errors(self, handler):
        """Test directory reading when some files have read errors."""
        mock_files = ["good_file.py", "bad_file.py"]

        def mock_read_file(file_path, file_name):
            if "bad_file" in file_name:
                raise Exception("Permission denied")
            return f"content of {file_name}"

        with patch.object(handler, '_get_all_files_recursively', return_value=mock_files), \
             patch.object(handler, '_read_local_file', side_effect=mock_read_file):

            result = await handler._read_local_directory("/path/to/directory", "test_dir")

            assert "Directory: test_dir" in result
            assert "Found 2 files (including subdirectories):" in result
            assert "--- File: good_file.py ---" in result
            assert "content of good_file.py" in result
            assert "--- File: bad_file.py (Error reading) ---" in result
            assert "Error: Permission denied" in result

    @pytest.mark.asyncio
    async def test_read_local_directory_error(self, handler):
        """Test directory reading with general error."""
        with patch.object(handler, '_get_all_files_recursively', side_effect=Exception("Directory error")):

            result = await handler._read_local_directory("/path/to/directory", "test_dir")

            assert "Error reading directory test_dir" in result

    def test_get_repository_name(self, handler):
        """Test repository name retrieval."""
        mock_entity = MagicMock()
        
        with patch('common.utils.utils.get_repository_name', return_value="test_repo") as mock_get_repo:
            result = handler._get_repository_name(mock_entity)
            
            assert result == "test_repo"
            mock_get_repo.assert_called_once_with(mock_entity)

    @pytest.mark.asyncio
    async def test_path_exists_true(self, handler):
        """Test path exists check when path exists."""
        with patch('asyncio.to_thread', new_callable=AsyncMock, return_value=True):
            result = await handler._path_exists("/existing/path")
            assert result is True

    @pytest.mark.asyncio
    async def test_path_exists_false(self, handler):
        """Test path exists check when path doesn't exist."""
        with patch('asyncio.to_thread', new_callable=AsyncMock, return_value=False):
            result = await handler._path_exists("/nonexistent/path")
            assert result is False

    @pytest.mark.asyncio
    async def test_path_exists_error(self, handler):
        """Test path exists check with error."""
        with patch('asyncio.to_thread', new_callable=AsyncMock, side_effect=Exception("OS error")):
            result = await handler._path_exists("/error/path")
            assert result is False

    @pytest.mark.asyncio
    async def test_is_directory_true(self, handler):
        """Test directory check when path is directory."""
        with patch('asyncio.to_thread', new_callable=AsyncMock, return_value=True):
            result = await handler._is_directory("/path/to/directory")
            assert result is True

    @pytest.mark.asyncio
    async def test_is_directory_false(self, handler):
        """Test directory check when path is file."""
        with patch('asyncio.to_thread', new_callable=AsyncMock, return_value=False):
            result = await handler._is_directory("/path/to/file.py")
            assert result is False

    @pytest.mark.asyncio
    async def test_is_directory_error(self, handler):
        """Test directory check with error."""
        with patch('asyncio.to_thread', new_callable=AsyncMock, side_effect=Exception("OS error")):
            result = await handler._is_directory("/error/path")
            assert result is False

    @pytest.mark.asyncio
    async def test_list_files_in_directory_success(self, handler):
        """Test successful file listing in directory."""
        mock_files = ["file1.py", "file2.java", ".hidden", "subdir"]

        def mock_listdir_sync():
            return ["file1.py", "file2.java", ".hidden", "subdir"]

        def mock_isfile(path):
            return not path.endswith("subdir") and not path.endswith(".hidden")

        with patch('asyncio.to_thread') as mock_to_thread:
            # Mock the sync function that gets called by asyncio.to_thread
            mock_to_thread.return_value = ["file1.py", "file2.java"]

            result = await handler._list_files_in_directory("/path/to/directory")

            assert result == ["file1.py", "file2.java"]

    @pytest.mark.asyncio
    async def test_list_files_in_directory_error(self, handler):
        """Test file listing with error."""
        with patch('asyncio.to_thread', new_callable=AsyncMock, side_effect=Exception("Permission denied")):
            result = await handler._list_files_in_directory("/error/directory")
            assert result == []

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

    # ===== JOBS TESTING SECTION =====

    @pytest.fixture
    def jobs_config(self):
        """Create a jobs configuration similar to extract_entities_from_prototype_22c6."""
        return {
            "type": "agent",
            "publish": False,
            "model": {"model_name": "gpt-4o-mini"},
            "max_iteration": 5,
            "approve": True,
            "memory_tags": ["get_entity_names_from_entities_requirement"],
            "jobs": [
                {
                    "type": "agent",
                    "publish": False,
                    "model": {},
                    "tools": [],
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName",
                        "input_file": "src/main/java/com/java_template/prototype/entities_requirement.json"
                    },
                    "memory_tags": ["get_entity_names_from_entities_requirement"],
                    "messages": [
                        {
                            "role": "user",
                            "content_from_file": "extract_entities_from_prototype_e7fa"
                        }
                    ],
                    "input": {
                        "local_fs": [
                            "src/main/java/com/java_template/prototype/entities_requirement.json"
                        ]
                    },
                    "output": "src/main/java/com/java_template/application/entity/{EntityName}.java",
                    "tool_choice": "auto",
                    "max_iteration": 5,
                    "approve": True
                }
            ]
        }

    @pytest.fixture
    def mock_split_function_registry(self):
        """Create mock method registry with split function."""
        class MockWorkflowClass:
            def __init__(self):
                self._function_registry = {
                    'get_entity_names_from_entities_requirement': AsyncMock(return_value=["User", "Product", "Order"])
                }

        mock_instance = MockWorkflowClass()
        return MethodRegistry(MockWorkflowClass, mock_instance)

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_success(self, mock_entity, mock_memory, jobs_config, mock_split_function_registry):
        """Test successful AI agent execution with jobs configuration."""
        # Create handler with mock split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User", "Product", "Order"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses for each entity
        ai_responses = ["User entity created", "Product entity created", "Order entity created"]
        handler.ai_agent.run_agent = AsyncMock(side_effect=ai_responses)

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        mock_messages = [AIMessage(role="user", content="Test message")]

        # Mock ConfigBuilder's _resolve_message_references method
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Enriched message content"}
        ])

        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:

            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify split function was called
            handler.method_registry.methods_dict[split_function_name].assert_called_once()

            # Verify AI agent was called for each entity
            assert handler.ai_agent.run_agent.call_count == len(entity_names)

            # Verify save_all was called with correct parameters
            mock_save_all.assert_called_once()
            call_args = mock_save_all.call_args[1]
            assert len(call_args['responses']) == len(entity_names)
            assert call_args['git_branch_id'] == mock_entity.branch_id
            # Repository name is resolved by _get_repository_name method, not directly from entity
            assert 'repository_name' in call_args

            # Verify response contains output paths for each entity
            expected_outputs = [
                "src/main/java/com/java_template/application/entity/User.java",
                "src/main/java/com/java_template/application/entity/Product.java",
                "src/main/java/com/java_template/application/entity/Order.java"
            ]
            assert result == "\n".join(expected_outputs)

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_split_function_error(self, mock_entity, mock_memory, jobs_config, mock_split_function_registry):
        """Test AI agent execution with jobs when split function fails."""
        # Create handler with mock split function that fails
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to raise an exception
        split_function_name = "get_entity_names_from_entities_requirement"
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(
            side_effect=Exception("Split function error")
        )

        with patch.object(handler, '_check_and_update_iteration', return_value=False):
            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Should return error message
            assert "Sorry, i'm having a little trouble with the LLM" in result

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_empty_split_result(self, mock_entity, mock_memory, jobs_config, mock_split_function_registry):
        """Test AI agent execution with jobs when split function returns empty list."""
        # Create handler with mock split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return empty list
        split_function_name = "get_entity_names_from_entities_requirement"
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=[])

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        with patch.object(handler, '_check_and_update_iteration', return_value=False):
            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify split function was called
            handler.method_registry.methods_dict[split_function_name].assert_called_once()

            # Verify AI agent was not called since no entities returned
            handler.ai_agent.run_agent.assert_not_called()

            # Should return "No files generated" when no entities
            assert result == "No files generated"

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_ai_agent_error(self, mock_entity, mock_memory, jobs_config, mock_split_function_registry):
        """Test AI agent execution with jobs when AI agent fails for one entity."""
        # Create handler with mock split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User", "Product"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent to fail on second call
        handler.ai_agent.run_agent = AsyncMock(side_effect=["User entity created", Exception("AI error")])

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        mock_messages = [AIMessage(role="user", content="Test message")]

        # Mock ConfigBuilder's _resolve_message_references method
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Enriched message content"}
        ])

        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:

            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # With the refactored code, individual job failures are handled gracefully
            # The system continues processing and returns successful results
            # Only the successful entity should be in the result
            assert "User.java" in result
            # The failed entity should not be in the result
            assert "Product.java" not in result

            # Verify save_all was called with only the successful response
            mock_save_all.assert_called_once()
            call_args = mock_save_all.call_args[1]
            assert len(call_args['responses']) == 1  # Only successful entity

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_multiple_jobs(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with multiple jobs in configuration."""
        # Create config with multiple jobs
        multi_jobs_config = {
            "type": "agent",
            "publish": False,
            "model": {"model_name": "gpt-4o-mini"},
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName",
                        "input_file": "entities_requirement.json"
                    },
                    "output": "entity/{EntityName}.java",
                    "tools": []
                },
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName",
                        "input_file": "entities_requirement.json"
                    },
                    "output": "dto/{EntityName}DTO.java",
                    "tools": []
                }
            ]
        }

        # Create handler with mock split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User", "Product"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(return_value="Generated successfully")

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        mock_messages = [AIMessage(role="user", content="Test message")]

        # Mock ConfigBuilder's _resolve_message_references method
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Enriched message content"}
        ])

        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:

            result = await handler.run_ai_agent(multi_jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify split function was called for each job
            assert handler.method_registry.methods_dict[split_function_name].call_count == 2

            # Verify AI agent was called for each entity in each job (2 jobs * 2 entities = 4 calls)
            assert handler.ai_agent.run_agent.call_count == 4

            # Verify save_all was called with correct parameters
            mock_save_all.assert_called_once()
            call_args = mock_save_all.call_args[1]
            assert len(call_args['responses']) == 4  # 2 jobs * 2 entities

            # Verify response contains output paths for both jobs
            expected_outputs = [
                "entity/User.java",  # First job, first entity
                "entity/Product.java",  # First job, second entity
                "dto/UserDTO.java",  # Second job, first entity
                "dto/ProductDTO.java"   # Second job, second entity
            ]
            assert result == "\n".join(expected_outputs)

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_parameter_formatting(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with jobs and parameter formatting in output."""
        # Create config with parameter formatting in output
        jobs_config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName",
                        "input_file": "entities_requirement.json"
                    },
                    "output": "src/main/java/com/example/entity/{EntityName}.java",
                    "tools": []
                }
            ]
        }

        # Create handler with mock split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User", "Product"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(return_value="Generated successfully")

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        mock_messages = [AIMessage(role="user", content="Test message")]

        # Mock ConfigBuilder's _resolve_message_references method
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Enriched message content"}
        ])

        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:

            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify save_all was called
            mock_save_all.assert_called_once()

            # Verify the output formatting - should format {EntityName} with actual entity values
            expected_outputs = [
                "src/main/java/com/example/entity/User.java",
                "src/main/java/com/example/entity/Product.java"
            ]
            assert result == "\n".join(expected_outputs)

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_memory_handling(self, mock_entity, mock_memory, jobs_config, mock_split_function_registry):
        """Test AI agent execution with jobs and proper memory handling."""
        # Create handler with mock split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(return_value="User entity created")

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        mock_messages = [AIMessage(role="user", content="Test message")]

        # Mock ConfigBuilder's _resolve_message_references method
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Enriched message content"}
        ])

        with patch.object(handler, '_check_and_update_iteration', return_value=False):

            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify memory operations were called correctly
            # Note: _append_messages is not called in jobs path - messages are handled via ConfigBuilder
            # Note: _get_ai_memory is not called in jobs path - messages are resolved directly from job config
            # Note: Memory storage is now handled at a higher level, not in AI agent handler

            # Verify ConfigBuilder was used for message resolution
            handler.config_builder._resolve_message_references.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_tool_configuration(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with jobs that have tool configurations."""
        # Create config with tools in job
        jobs_config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "tools": [
                        {"name": "save_file"},
                        {"name": "read_file"}
                    ],
                    "tool_choice": "auto",
                    "output": "{EntityName}.java"
                }
            ]
        }

        # Create handler with mock split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(return_value="User entity created")

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        mock_messages = [AIMessage(role="user", content="Test message")]

        # Mock ConfigBuilder's _resolve_message_references method
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Enriched message content"}
        ])

        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:

            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify save_all was called
            mock_save_all.assert_called_once()

            # Verify AI agent was called with correct tools configuration
            handler.ai_agent.run_agent.assert_called_once()
            call_args = handler.ai_agent.run_agent.call_args
            assert call_args[1]['tools'] == [{"name": "save_file"}, {"name": "read_file"}]
            assert call_args[1]['tool_choice'] == "auto"

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_model_configuration(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with jobs that have model configurations."""
        # Create config with model in job
        jobs_config = {
            "type": "agent",
            "model": {"model_name": "gpt-4o", "temperature": 0.7},  # Parent model config
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "model": {"model_name": "gpt-4o-mini", "temperature": 0.5},  # Job-specific model config
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "output": "{EntityName}.java"
                }
            ]
        }

        # Create handler with mock split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(return_value="User entity created")

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        mock_messages = [AIMessage(role="user", content="Test message")]

        # Mock ConfigBuilder's _resolve_message_references method
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Enriched message content"}
        ])

        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:

            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify save_all was called
            mock_save_all.assert_called_once()

            # Verify AI agent was called with parent model config (not job-specific)
            handler.ai_agent.run_agent.assert_called_once()
            call_args = handler.ai_agent.run_agent.call_args
            model_config = call_args[1]['model']
            assert model_config.model_name == "gpt-4o"  # Should use parent config
            assert model_config.temperature == 0.7

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_real_extract_entities_config(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with the real extract_entities_from_prototype_22c6 config."""
        # Load the real config file
        import json
        import os

        config_path = "workflow_configs/agents/extract_entities_from_prototype_22c6/agent.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                real_config = json.load(f)
        else:
            # Fallback to the config structure we know
            real_config = {
                "type": "agent",
                "publish": False,
                "model": {},
                "max_iteration": 5,
                "approve": True,
                "jobs": [
                    {
                        "type": "agent",
                        "publish": False,
                        "model": {},
                        "tools": [],
                        "split_function": {
                            "name": "get_entity_names_from_entities_requirement",
                            "split_parameter": "EntityName",
                            "input_file": "src/main/java/com/java_template/prototype/entities_requirement.json"
                        },
                        "memory_tags": ["get_entity_names_from_entities_requirement"],
                        "messages": [
                            {
                                "role": "user",
                                "content_from_file": "extract_entities_from_prototype_e7fa"
                            }
                        ],
                        "input": {
                            "local_fs": [
                                "src/main/java/com/java_template/prototype/entities_requirement.json"
                            ]
                        },
                        "output": "src/main/java/com/java_template/application/entity/{EntityName}.java",
                        "tool_choice": "auto",
                        "max_iteration": 5,
                        "approve": True
                    }
                ]
            }

        # Create handler with mock split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User", "Product", "Order"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(return_value="Entity created successfully")

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        mock_messages = [AIMessage(role="user", content="Extract entities from prototype")]

        # Mock ConfigBuilder's _resolve_message_references method
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Extract entities from prototype"}
        ])

        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:

            result = await handler.run_ai_agent(real_config, mock_entity, mock_memory, "tech_id")

            # Verify split function was called with correct parameters
            handler.method_registry.methods_dict[split_function_name].assert_called_once()
            call_args = handler.method_registry.methods_dict[split_function_name].call_args
            assert call_args[1]['params']['input_file'] == "src/main/java/com/java_template/prototype/entities_requirement.json"

            # Verify AI agent was called for each entity
            assert handler.ai_agent.run_agent.call_count == len(entity_names)

            # Verify save_all was called
            mock_save_all.assert_called_once()

            # Verify response contains expected output paths
            expected_outputs = [
                "src/main/java/com/java_template/application/entity/User.java",
                "src/main/java/com/java_template/application/entity/Product.java",
                "src/main/java/com/java_template/application/entity/Order.java"
            ]
            assert result == "\n".join(expected_outputs)

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_missing_split_function(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with jobs when split function is missing from registry."""
        # Create config with non-existent split function
        jobs_config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "non_existent_function",
                        "split_parameter": "EntityName"
                    },
                    "output": "{EntityName}.java"
                }
            ]
        }

        # Create handler without the split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        with patch.object(handler, '_check_and_update_iteration', return_value=False):
            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Should return error message due to missing function
            assert "Sorry, i'm having a little trouble with the LLM" in result

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_iteration_limit_exceeded(self, mock_entity, mock_memory, jobs_config, mock_split_function_registry):
        """Test AI agent execution with jobs when iteration limit is exceeded."""
        # Create handler with mock split function
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock iteration check to return True (exceeded)
        with patch.object(handler, '_check_and_update_iteration', return_value=True):
            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Should return iteration exceeded message
            assert "Let's proceed to the next iteration" in result

            # Verify no jobs were processed
            handler.ai_agent.run_agent.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_message_enrichment(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with jobs and message enrichment from content_from_file."""
        # Create config with content_from_file in messages
        jobs_config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "messages": [
                        {
                            "role": "user",
                            "content_from_file": "extract_entities_prompt"
                        }
                    ],
                    "output": "{EntityName}.java"
                }
            ]
        }

        # Create handler
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(return_value="User entity created")

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        # Mock ConfigBuilder's _resolve_message_references method to simulate content_from_file resolution
        resolved_messages = [
            {
                "role": "user",
                "content": ["You are an expert Java developer. Extract entity classes from the prototype."]
            }
        ]
        handler.config_builder._resolve_message_references = MagicMock(return_value=resolved_messages)

        with patch.object(handler, '_check_and_update_iteration', return_value=False):
            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify ConfigBuilder's _resolve_message_references was called
            handler.config_builder._resolve_message_references.assert_called_once()
            call_args = handler.config_builder._resolve_message_references.call_args[0][0]
            assert call_args[0]["content_from_file"] == "extract_entities_prompt"

            # Verify AI agent was called with enriched message
            handler.ai_agent.run_agent.assert_called_once()
            ai_call_args = handler.ai_agent.run_agent.call_args[1]
            messages = ai_call_args['messages']
            assert len(messages) == 1
            assert messages[0].role == "user"
            assert "You are an expert Java developer" in messages[0].content

            # Verify response contains output path
            assert result == "User.java"

    @pytest.mark.asyncio
    async def test_config_builder_integration(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test that ConfigBuilder is properly integrated and used for message resolution."""
        from workflow.config_builder import ConfigBuilder

        # Create a real ConfigBuilder instance for testing
        config_builder = ConfigBuilder()

        # Create handler with real ConfigBuilder
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock(),
            config_builder=config_builder
        )

        # Mock the split function
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent
        handler.ai_agent.run_agent = AsyncMock(return_value="User entity created")
        handler.memory_manager.store_ai_response = AsyncMock()

        # Test with content_from_file that should be resolved
        jobs_config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "messages": [
                        {
                            "role": "user",
                            "content_from_file": "nonexistent_prompt"  # This will trigger the fallback behavior
                        }
                    ],
                    "output": "{EntityName}.java"
                }
            ]
        }

        # Mock the _load_prompt_content method to simulate file not found
        with patch.object(config_builder, '_load_prompt_content', side_effect=FileNotFoundError("Prompt not found")):
            with patch.object(handler, '_check_and_update_iteration', return_value=False):
                result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

                # Verify that the ConfigBuilder was used and handled the missing file gracefully
                handler.ai_agent.run_agent.assert_called_once()
                call_args = handler.ai_agent.run_agent.call_args[1]
                messages = call_args['messages']

                # The message should still contain the original content_from_file reference
                # since ConfigBuilder keeps the original message when file is not found
                assert len(messages) == 1
                assert messages[0].role == "user"
                # The content should be empty string since content_from_file wasn't resolved
                assert messages[0].content == ""

                assert result == "User.java"

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_save_all_functionality(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with jobs and save_all functionality."""
        # Create config with jobs
        jobs_config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "messages": [{"role": "user", "content": "Generate entity"}],
                    "output": "src/main/java/entity/{EntityName}.java"
                }
            ]
        }

        # Create handler
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User", "Product"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(side_effect=["User entity code", "Product entity code"])

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        # Mock ConfigBuilder
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Generate entity"}
        ])

        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:

            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify save_all was called with correct parameters
            mock_save_all.assert_called_once()
            call_args = mock_save_all.call_args[1]

            # Check responses structure
            responses = call_args['responses']
            assert len(responses) == 2
            assert responses[0]['output_path'] == "src/main/java/entity/User.java"
            assert responses[0]['data'] == "User entity code"
            assert responses[1]['output_path'] == "src/main/java/entity/Product.java"
            assert responses[1]['data'] == "Product entity code"

            # Check git parameters
            assert call_args['git_branch_id'] == mock_entity.branch_id
            # Repository name is resolved by _get_repository_name method
            assert 'repository_name' in call_args
            assert "Generated 2 files from get_entity_names_from_entities_requirement" in call_args['commit_message']

            # Verify response contains output paths
            expected_outputs = [
                "src/main/java/entity/User.java",
                "src/main/java/entity/Product.java"
            ]
            assert result == "\n".join(expected_outputs)

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_save_all_failure(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with jobs when save_all fails."""
        # Create config with jobs
        jobs_config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "messages": [{"role": "user", "content": "Generate entity"}],
                    "output": "{EntityName}.java"
                }
            ]
        }

        # Create handler
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(return_value="User entity code")

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        # Mock ConfigBuilder
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Generate entity"}
        ])

        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=False) as mock_save_all:

            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify save_all was called
            mock_save_all.assert_called_once()

            # Should return error message when save fails
            assert result == "Error: Failed to save generated files"

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_input_files(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with jobs that have input files."""
        # Create config with input files
        jobs_config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "messages": [{"role": "user", "content": "Generate entity based on requirements"}],
                    "input": {
                        "local_fs": [
                            "src/main/java/com/java_template/prototype/entities_requirement.json"
                        ]
                    },
                    "output": "{EntityName}.java"
                }
            ]
        }

        # Create handler
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(return_value="User entity code")

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        # Mock ConfigBuilder
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Generate entity based on requirements"}
        ])

        # Mock the input file reading
        mock_input_content = '''{"entities": [{"name": "User", "fields": ["id", "name", "email"]}]}'''

        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all, \
             patch.object(handler.jobs_processor, '_read_input_files', new_callable=AsyncMock, return_value=mock_input_content) as mock_read_files:

            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify input files were read
            mock_read_files.assert_called_once_with(
                ["src/main/java/com/java_template/prototype/entities_requirement.json"],
                mock_entity
            )

            # Verify AI agent was called with messages including input file content
            handler.ai_agent.run_agent.assert_called_once()
            call_args = handler.ai_agent.run_agent.call_args[1]
            messages = call_args['messages']

            # Should have original message plus system message with input file content
            assert len(messages) >= 2

            # Check that input file content was appended as system message
            system_messages = [msg for msg in messages if msg.role == "system"]
            assert len(system_messages) == 1
            assert "Input files content:" in system_messages[0].content
            assert mock_input_content in system_messages[0].content

            # Verify save_all was called
            mock_save_all.assert_called_once()

            # Verify response contains output path
            assert result == "User.java"

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_input_files_error(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with jobs when input file reading fails."""
        # Create config with input files
        jobs_config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "messages": [{"role": "user", "content": "Generate entity"}],
                    "input": {
                        "local_fs": ["nonexistent_file.json"]
                    },
                    "output": "{EntityName}.java"
                }
            ]
        }

        # Create handler
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        # Mock the split function to return entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        handler.method_registry.methods_dict[split_function_name] = AsyncMock(return_value=entity_names)

        # Mock AI agent responses
        handler.ai_agent.run_agent = AsyncMock(return_value="User entity code")

        # Mock memory manager
        handler.memory_manager.store_ai_response = AsyncMock()

        # Mock ConfigBuilder
        handler.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Generate entity"}
        ])

        # Mock input file reading to return empty (simulating error)
        with patch.object(handler, '_check_and_update_iteration', return_value=False), \
             patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all, \
             patch.object(handler.jobs_processor, '_read_input_files', new_callable=AsyncMock, return_value="") as mock_read_files:

            result = await handler.run_ai_agent(jobs_config, mock_entity, mock_memory, "tech_id")

            # Verify input files were attempted to be read
            mock_read_files.assert_called_once_with(["nonexistent_file.json"], mock_entity)

            # Verify AI agent was still called (should continue even if input files fail)
            handler.ai_agent.run_agent.assert_called_once()
            call_args = handler.ai_agent.run_agent.call_args[1]
            messages = call_args['messages']

            # Should have original message only (no system message since input file reading failed)
            user_messages = [msg for msg in messages if msg.role == "user"]
            assert len(user_messages) == 1

            # Verify save_all was called
            mock_save_all.assert_called_once()

            # Verify response contains output path
            assert result == "User.java"

    @pytest.mark.asyncio
    async def test_run_ai_agent_with_jobs_batch_processing(self, mock_entity, mock_memory, mock_split_function_registry):
        """Test AI agent execution with batch processing type."""
        # Create batch processing config
        batch_config = {
            "type": "batch",
            "input": {
                "local_fs": ["input.jsonl"]
            },
            "output": {
                "local_fs": ["output.jsonl"]
            }
        }

        # Create handler
        handler = AIAgentHandler(
            ai_agent=AsyncMock(),
            method_registry=mock_split_function_registry,
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=mock_split_function_registry.cls_instance,
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

        with patch.object(handler, '_handle_batch_processing', return_value="Batch processing completed") as mock_batch:
            result = await handler.run_ai_agent(batch_config, mock_entity, mock_memory, "tech_id")

            # Should call batch processing handler
            mock_batch.assert_called_once_with(batch_config)
            assert result == "Batch processing completed"

            # Verify regular AI agent was not called
            handler.ai_agent.run_agent.assert_not_called()
