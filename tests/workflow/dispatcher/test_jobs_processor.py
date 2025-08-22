import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import common.config.const as const
from entity.model import AgenticFlowEntity, ChatMemory, TransitionsMemory, AIMessage
from workflow.dispatcher.jobs_processor import JobsProcessor
from workflow.dispatcher.memory_manager import MemoryManager


class TestJobsProcessor:
    """Test cases for JobsProcessor class."""

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
        # Add attributes needed for jobs functionality
        entity.branch_id = "test_branch"
        entity.repository_name = "test_repo"
        entity.workflow_name = "java_template"
        return entity

    @pytest.fixture
    def mock_memory(self):
        """Create mock ChatMemory."""
        memory = MagicMock(spec=ChatMemory)
        memory.messages = {
            "test_memory_id": []
        }
        return memory

    @pytest.fixture
    def jobs_processor(self):
        """Create JobsProcessor instance."""
        return JobsProcessor(
            ai_agent=AsyncMock(),
            method_registry=MagicMock(),
            memory_manager=MagicMock(spec=MemoryManager),
            cls_instance=MagicMock(),
            entity_service=AsyncMock(),
            cyoda_auth_service=MagicMock()
        )

    @pytest.mark.asyncio
    async def test_process_jobs_success(self, jobs_processor, mock_entity, mock_memory):
        """Test successful jobs processing."""
        # Create jobs config
        config = {
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

        # Mock split function
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User", "Product"]
        jobs_processor.method_registry.methods_dict = {
            split_function_name: AsyncMock(return_value=entity_names)
        }

        # Mock AI agent responses
        jobs_processor.ai_agent.run_agent = AsyncMock(side_effect=["User code", "Product code"])

        # Mock ConfigBuilder
        jobs_processor.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Generate entity for EntityName={split_parameter_value}"}
        ])

        with patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:
            result = await jobs_processor.process_jobs(config, mock_entity, mock_memory, "tech_id")

            # Verify split function was called
            jobs_processor.method_registry.methods_dict[split_function_name].assert_called_once()

            # Verify AI agent was called for each entity
            assert jobs_processor.ai_agent.run_agent.call_count == len(entity_names)

            # Verify save_all was called
            mock_save_all.assert_called_once()
            call_args = mock_save_all.call_args[1]
            assert len(call_args['responses']) == len(entity_names)

            # Verify response contains output paths
            expected_outputs = ["User.java", "Product.java"]
            assert result == "\n".join(expected_outputs)

    @pytest.mark.asyncio
    async def test_process_jobs_with_input_files(self, jobs_processor, mock_entity, mock_memory):
        """Test jobs processing with input files."""
        # Create jobs config with input files
        config = {
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
                        "local_fs": ["entities_requirement.json"]
                    },
                    "output": "{EntityName}.java"
                }
            ]
        }

        # Mock split function
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        jobs_processor.method_registry.methods_dict = {
            split_function_name: AsyncMock(return_value=entity_names)
        }

        # Mock AI agent responses
        jobs_processor.ai_agent.run_agent = AsyncMock(return_value="User code")

        # Mock ConfigBuilder
        jobs_processor.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Generate entity"}
        ])

        # Mock input file reading
        mock_input_content = '{"entities": [{"name": "User"}]}'

        with patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all, \
             patch.object(jobs_processor, '_read_input_files', new_callable=AsyncMock, return_value=mock_input_content) as mock_read_files:

            result = await jobs_processor.process_jobs(config, mock_entity, mock_memory, "tech_id")

            # Verify input files were read
            mock_read_files.assert_called_once_with(["entities_requirement.json"], mock_entity)

            # Verify AI agent was called with enriched messages
            jobs_processor.ai_agent.run_agent.assert_called_once()
            call_args = jobs_processor.ai_agent.run_agent.call_args[1]
            messages = call_args['messages']

            # Should have original message plus system message with input file content
            assert len(messages) >= 2
            system_messages = [msg for msg in messages if msg.role == "system"]
            assert len(system_messages) == 1
            assert "Input files content:" in system_messages[0].content
            assert mock_input_content in system_messages[0].content

            # Verify save_all was called
            mock_save_all.assert_called_once()

            # Verify response
            assert result == "User.java"

    @pytest.mark.asyncio
    async def test_parameter_formatting_in_messages(self, jobs_processor, mock_entity, mock_memory):
        """Test that message content is properly formatted with entity values."""
        # Create jobs config with parameter formatting
        config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "messages": [{"role": "user", "content": "Please return Entity Pojo for EntityName={split_parameter_value} from the requirements document.\nEntity POJO template:\npackage com.java_template.application.entity.{entityName}.version_1; // replace {entityName} with actual entity name in lowercase\n\n@Data\npublic class {EntityName} implements CyodaEntity { // replace {EntityName} with actual entity name in camel case\n    public static final String ENTITY_NAME = \"{EntityName}\";  // replace {EntityName} with actual entity name in camel case"}],
                    "output": "{EntityName}.java"
                }
            ]
        }

        # Mock split function
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        jobs_processor.method_registry.methods_dict = {
            split_function_name: AsyncMock(return_value=entity_names)
        }

        # Mock AI agent responses
        jobs_processor.ai_agent.run_agent = AsyncMock(return_value="User entity code")

        # Mock ConfigBuilder
        jobs_processor.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Please return Entity Pojo for EntityName={split_parameter_value} from the requirements document.\nEntity POJO template:\npackage com.java_template.application.entity.{entityName}.version_1; // replace {entityName} with actual entity name in lowercase\n\n@Data\npublic class {EntityName} implements CyodaEntity { // replace {EntityName} with actual entity name in camel case\n    public static final String ENTITY_NAME = \"{EntityName}\";  // replace {EntityName} with actual entity name in camel case"}
        ])

        with patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:
            result = await jobs_processor.process_jobs(config, mock_entity, mock_memory, "tech_id")

            # Verify AI agent was called with properly formatted messages
            jobs_processor.ai_agent.run_agent.assert_called_once()
            call_args = jobs_processor.ai_agent.run_agent.call_args[1]
            messages = call_args['messages']

            # Check that the message content was properly formatted
            user_message = messages[0]
            assert user_message.role == "user"
            expected_content = "Please return Entity Pojo for EntityName=User from the requirements document.\nEntity POJO template:\npackage com.java_template.application.entity.{entityName}.version_1; // replace {entityName} with actual entity name in lowercase\n\n@Data\npublic class {EntityName} implements CyodaEntity { // replace {EntityName} with actual entity name in camel case\n    public static final String ENTITY_NAME = \"{EntityName}\";  // replace {EntityName} with actual entity name in camel case"
            assert user_message.content == expected_content

            # Verify response
            assert result == "User.java"

    @pytest.mark.asyncio
    async def test_process_jobs_with_real_config_data(self, jobs_processor):
        """Test jobs processing with real configuration data from backup/test."""
        import ast

        # Load real config from backup/test/config.txt
        with open('/home/kseniia/PycharmProjects/ai_assistant/backup/test/config.txt', 'r') as f:
            config_str = f.read().strip()
            config = ast.literal_eval(config_str)

        # Load real entity from backup/test/entity
        with open('/home/kseniia/PycharmProjects/ai_assistant/backup/test/entity', 'r') as f:
            entity_str = f.read().strip()
            # Parse the entity string to extract key information
            # For testing, we'll create a mock entity with the essential attributes
            mock_entity = MagicMock()
            mock_entity.workflow_cache = {
                'git_branch': '1bcbec5a-2a85-11b2-a79b-1a87e208ff0a',
                'repository_name': 'java-client-template'
            }
            mock_entity.workflow_name = 'build_general_application_java'
            mock_entity.technical_id = '1bcbec5a-2a85-11b2-a79b-1a87e208ff0a'

        # Load real memory from backup/test/memory
        with open('/home/kseniia/PycharmProjects/ai_assistant/backup/test/memory', 'r') as f:
            memory_str = f.read().strip()
            mock_memory = MagicMock()
            mock_memory.technical_id = '11e3398c-2a85-11b2-a79b-1a87e208ff0a'

        # Mock split function to return some entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["Pet", "Owner", "Appointment"]
        jobs_processor.method_registry.methods_dict = {
            split_function_name: AsyncMock(return_value=entity_names)
        }

        # Mock AI agent responses
        jobs_processor.ai_agent.run_agent = AsyncMock(side_effect=[
            "Pet entity code", "Owner entity code", "Appointment entity code"
        ])

        # Mock ConfigBuilder to return a message with parameter formatting
        jobs_processor.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Please return Entity Pojo for EntityName={split_parameter_value} from the requirements document."}
        ])

        with patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:
            result = await jobs_processor.process_jobs(config, mock_entity, mock_memory, "tech_id")

            # Verify split function was called
            jobs_processor.method_registry.methods_dict[split_function_name].assert_called_once()

            # Verify AI agent was called for each entity (should be concurrent)
            assert jobs_processor.ai_agent.run_agent.call_count == len(entity_names)

            # Verify save_all was called
            mock_save_all.assert_called_once()
            call_args = mock_save_all.call_args[1]
            assert len(call_args['responses']) == len(entity_names)

            # Verify response contains expected output paths
            expected_outputs = [
                "src/main/java/com/java_template/application/entity/Pet.java",
                "src/main/java/com/java_template/application/entity/Owner.java",
                "src/main/java/com/java_template/application/entity/Appointment.java"
            ]
            assert result == "\n".join(expected_outputs)

    @pytest.mark.asyncio
    async def test_async_concurrent_processing(self, jobs_processor, mock_entity, mock_memory):
        """Test that jobs and values are processed concurrently using async tasks."""
        # Create config with multiple jobs and multiple entities per job
        config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "messages": [{"role": "user", "content": "Generate entity {split_parameter_value}"}],
                    "output": "entity/{EntityName}.java"
                },
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "messages": [{"role": "user", "content": "Generate DTO for {split_parameter_value}"}],
                    "output": "dto/{EntityName}DTO.java"
                }
            ]
        }

        # Mock split function to return multiple entity names
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User", "Product", "Order"]
        jobs_processor.method_registry.methods_dict = {
            split_function_name: AsyncMock(return_value=entity_names)
        }

        # Mock AI agent responses - should be called 6 times (2 jobs * 3 entities)
        jobs_processor.ai_agent.run_agent = AsyncMock(side_effect=[
            "User entity", "Product entity", "Order entity",
            "User DTO", "Product DTO", "Order DTO"
        ])

        # Mock ConfigBuilder - will be called 6 times (2 jobs * 3 entities)
        # First 3 calls for entity job, next 3 calls for DTO job
        jobs_processor.config_builder._resolve_message_references = MagicMock(side_effect=[
            [{"role": "user", "content": "Generate entity {split_parameter_value}"}],  # User entity
            [{"role": "user", "content": "Generate entity {split_parameter_value}"}],  # Product entity
            [{"role": "user", "content": "Generate entity {split_parameter_value}"}],  # Order entity
            [{"role": "user", "content": "Generate DTO for {split_parameter_value}"}],  # User DTO
            [{"role": "user", "content": "Generate DTO for {split_parameter_value}"}],  # Product DTO
            [{"role": "user", "content": "Generate DTO for {split_parameter_value}"}]   # Order DTO
        ])

        with patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:
            result = await jobs_processor.process_jobs(config, mock_entity, mock_memory, "tech_id")

            # Verify split function was called for each job
            assert jobs_processor.method_registry.methods_dict[split_function_name].call_count == 2

            # Verify AI agent was called for all combinations (2 jobs * 3 entities = 6 calls)
            assert jobs_processor.ai_agent.run_agent.call_count == 6

            # Verify save_all was called with all responses
            mock_save_all.assert_called_once()
            call_args = mock_save_all.call_args[1]
            assert len(call_args['responses']) == 6  # 2 jobs * 3 entities

            # Verify response contains all output paths
            expected_outputs = [
                "entity/User.java", "entity/Product.java", "entity/Order.java",
                "dto/UserDTO.java", "dto/ProductDTO.java", "dto/OrderDTO.java"
            ]
            # The order might vary due to async processing, so check all are present
            result_lines = result.split("\n")
            assert len(result_lines) == 6
            for expected_output in expected_outputs:
                assert expected_output in result_lines

    @pytest.mark.asyncio
    async def test_output_path_formatting(self, jobs_processor, mock_entity, mock_memory):
        """Test that output paths are properly formatted with entity values."""
        # Create jobs config with complex output path formatting
        config = {
            "type": "agent",
            "memory_tags": ["test_memory"],
            "jobs": [
                {
                    "type": "agent",
                    "split_function": {
                        "name": "get_entity_names_from_entities_requirement",
                        "split_parameter": "EntityName"
                    },
                    "messages": [{"role": "user", "content": "Generate workflow for {EntityName}"}],
                    "output": "src/main/resources/workflow/{entityname}/version_1/{EntityName}.json"
                }
            ]
        }

        # Mock split function
        split_function_name = "get_entity_names_from_entities_requirement"
        entity_names = ["User"]
        jobs_processor.method_registry.methods_dict = {
            split_function_name: AsyncMock(return_value=entity_names)
        }

        # Mock AI agent responses
        jobs_processor.ai_agent.run_agent = AsyncMock(return_value='{"workflow": "User workflow"}')

        # Mock ConfigBuilder
        jobs_processor.config_builder._resolve_message_references = MagicMock(return_value=[
            {"role": "user", "content": "Generate workflow for {EntityName}"}
        ])

        with patch('workflow.dispatcher.jobs_processor.save_all', new_callable=AsyncMock, return_value=True) as mock_save_all:
            result = await jobs_processor.process_jobs(config, mock_entity, mock_memory, "tech_id")

            # Verify save_all was called with properly formatted output path
            mock_save_all.assert_called_once()
            call_args = mock_save_all.call_args[1]
            responses = call_args['responses']

            assert len(responses) == 1
            expected_output_path = "src/main/resources/workflow/user/version_1/User.json"
            assert responses[0]['output_path'] == expected_output_path

            # Verify response contains the formatted output path
            assert result == expected_output_path

    @pytest.mark.asyncio
    async def test_get_git_branch_id(self, jobs_processor, mock_entity):
        """Test git branch ID extraction from entity."""
        # Test with valid branch ID
        branch_id = jobs_processor._get_git_branch_id(mock_entity)
        assert branch_id == "test_branch"

        # Test with missing branch ID
        mock_entity.workflow_cache = {}
        branch_id = jobs_processor._get_git_branch_id(mock_entity)
        assert branch_id is None

    @pytest.mark.asyncio
    async def test_read_input_files_error_handling(self, jobs_processor, mock_entity):
        """Test input file reading with error handling."""
        file_paths = ["nonexistent_file.json"]

        # Mock clone_repo and os.path.exists to simulate file not found
        with patch('workflow.dispatcher.jobs_processor.clone_repo', new_callable=AsyncMock), \
             patch('workflow.dispatcher.jobs_processor.os.path.exists', return_value=False):
            result = await jobs_processor._read_input_files(file_paths, mock_entity)
            expected = "=== nonexistent_file.json ===\n[File not found]"
            assert result == expected

    @pytest.mark.asyncio
    async def test_read_input_files_clone_failure(self, jobs_processor, mock_entity):
        """Test input file reading when clone_repo fails."""
        file_paths = ["test_file.json"]

        # Mock clone_repo to raise an exception
        with patch('workflow.dispatcher.jobs_processor.clone_repo', new_callable=AsyncMock, side_effect=Exception("Clone failed")):
            result = await jobs_processor._read_input_files(file_paths, mock_entity)
            assert result == ""

    @pytest.mark.asyncio
    async def test_save_and_commit_responses_no_responses(self, jobs_processor, mock_entity):
        """Test save and commit with no responses."""
        result = await jobs_processor._save_and_commit_responses([], [], mock_entity)
        assert result == "No files generated"

    @pytest.mark.asyncio
    async def test_save_and_commit_responses_missing_repo_info(self, jobs_processor):
        """Test save and commit with missing repository information."""
        # Create entity without branch_id but with workflow_name
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {}  # Missing GIT_BRANCH_PARAM
        entity.workflow_name = "java_template"  # Required for get_repository_name

        responses = [{"output_path": "test.java", "data": "test code"}]
        jobs = [{"split_function": {"name": "test_job"}}]

        result = await jobs_processor._save_and_commit_responses(responses, jobs, entity)
        assert "Warning: Generated content but could not save files" in result
