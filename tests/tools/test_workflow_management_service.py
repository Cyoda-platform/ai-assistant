import json
import os
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from tools.workflow_management_service import WorkflowManagementService
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
import common.config.const as const


class TestWorkflowManagementService:
    """Test cases for WorkflowManagementService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for WorkflowManagementService."""
        return {
            'workflow_helper_service': AsyncMock(),
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
            'workflow_converter_service': AsyncMock(),
            'scheduler_service': AsyncMock(),
            'data_service': AsyncMock(),
        }

    @pytest.fixture
    def service(self, mock_dependencies):
        """Create WorkflowManagementService instance."""
        return WorkflowManagementService(**mock_dependencies)

    @pytest.fixture
    def mock_chat_entity(self):
        """Create mock ChatEntity."""
        entity = MagicMock(spec=ChatEntity)
        entity.workflow_cache = {
            const.GIT_BRANCH_PARAM: "test_branch",
            "entity_name": "test_entity"
        }
        entity.workflow_name = "test_workflow"
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
        return entity

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {
            const.GIT_BRANCH_PARAM: "test_branch",
            "workflow_function": "test_function",
            "entity_name": "test_entity"
        }
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
        entity.workflow_name = "test_workflow_python"
        entity.scheduled_entities = []
        entity.edge_messages_store = {"test_transition": "edge_message_123"}
        return entity

    @pytest.mark.asyncio
    async def test_register_workflow_with_app_success(self, service, mock_agentic_entity):
        """Test successful workflow registration with app."""
        # Mock external dependencies
        mock_file_content = '{"entity_models": [{"entity_model_name": "test", "workflow_function": {"name": "test_func"}}], "file_without_workflow": {"code": "test_code"}}'

        def mock_aiofiles_open(*args, **kwargs):
            mock_file = AsyncMock()
            mock_file.read = AsyncMock(return_value=mock_file_content)
            mock_file.__aenter__ = AsyncMock(return_value=mock_file)
            mock_file.__aexit__ = AsyncMock(return_value=None)
            return mock_file

        with patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/file.json"), \
             patch('aiofiles.open', side_effect=mock_aiofiles_open), \
             patch('common.utils.utils._save_file', new_callable=AsyncMock), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            service.entity_service.add_item = AsyncMock(return_value="edge_message_123")
            service.workflow_helper_service.launch_agentic_workflow = AsyncMock(return_value="child_tech_id")
            service.workflow_helper_service.launch_scheduled_workflow = AsyncMock(return_value="scheduled_id")

            result = await service.register_workflow_with_app(
                "tech_id", mock_agentic_entity,
                filename="test.json",
                routes_file="routes.py"
            )

            assert result == "Workflow registration completed successfully"

    @pytest.mark.asyncio
    async def test_register_workflow_with_app_error(self, service, mock_agentic_entity):
        """Test workflow registration with error."""
        # Mock external dependencies to cause an error
        with patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, side_effect=Exception("File error")):

            result = await service.register_workflow_with_app(
                "tech_id", mock_agentic_entity,
                filename="test.json",
                routes_file="routes.py"
            )

            assert "Error registering workflow" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_validate_workflow_design_success(self, service, mock_agentic_entity):
        """Test successful workflow design validation."""
        # Mock entity service to return validation result
        service.entity_service.get_item = AsyncMock(return_value="validation_result")

        # Mock validate_ai_result to return success
        with patch('tools.workflow_management_service.validate_ai_result', return_value=(True, "Validation passed")):
            result = await service.validate_workflow_design(
                "tech_id", mock_agentic_entity,
                transition="test_transition"
            )

            assert result == "Validation passed"

    @pytest.mark.asyncio
    async def test_validate_workflow_design_error(self, service, mock_agentic_entity):
        """Test workflow design validation with error."""
        # Mock entity service to raise an exception
        service.entity_service.get_item = AsyncMock(side_effect=Exception("Validation error"))

        result = await service.validate_workflow_design(
            "tech_id", mock_agentic_entity,
            transition="test_transition"
        )

        # Method returns None on error
        assert result is None

    @pytest.mark.asyncio
    async def test_has_workflow_code_validation_succeeded_true(self, service, mock_agentic_entity):
        """Test workflow code validation success check when succeeded."""
        # Mock entity service to return a result (indicating success)
        service.entity_service.get_item = AsyncMock(return_value="validation_result")

        result = await service.has_workflow_code_validation_succeeded(
            "tech_id", mock_agentic_entity,
            transition="test_transition"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_has_workflow_code_validation_succeeded_false(self, service, mock_agentic_entity):
        """Test workflow code validation success check when failed."""
        # Mock entity service to return None (indicating failure)
        service.entity_service.get_item = AsyncMock(return_value=None)

        result = await service.has_workflow_code_validation_succeeded(
            "tech_id", mock_agentic_entity,
            transition="test_transition"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_has_workflow_code_validation_succeeded_error(self, service, mock_agentic_entity):
        """Test workflow code validation success check with error."""
        # Mock entity service to raise an exception
        service.entity_service.get_item = AsyncMock(side_effect=Exception("Check error"))

        result = await service.has_workflow_code_validation_succeeded(
            "tech_id", mock_agentic_entity,
            transition="test_transition"
        )

        # Method returns False on error
        assert result is False

    @pytest.mark.asyncio
    async def test_has_workflow_code_validation_failed_true(self, service, mock_agentic_entity):
        """Test workflow code validation failure check when failed."""
        # Mock entity service to return None (indicating failure, so failed = True)
        service.entity_service.get_item = AsyncMock(return_value=None)

        result = await service.has_workflow_code_validation_failed(
            "tech_id", mock_agentic_entity,
            transition="test_transition"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_has_workflow_code_validation_failed_false(self, service, mock_agentic_entity):
        """Test workflow code validation failure check when succeeded."""
        # Mock entity service to return a result (indicating success, so failed = False)
        service.entity_service.get_item = AsyncMock(return_value="validation_result")

        result = await service.has_workflow_code_validation_failed(
            "tech_id", mock_agentic_entity,
            transition="test_transition"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_save_extracted_workflow_code_success(self, service, mock_agentic_entity):
        """Test successful extracted workflow code saving."""
        # Mock external dependencies
        service.entity_service.get_item = AsyncMock(return_value="source_code")

        with patch('common.utils.function_extractor.extract_function', return_value=("code_without_function", "extracted_function")), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"), \
             patch('common.utils.utils._save_file', new_callable=AsyncMock):

            result = await service.save_extracted_workflow_code(
                "tech_id", mock_agentic_entity,
                transition="test_transition"
            )

            # The method returns empty string when no extraction is performed
            assert result == ""

    @pytest.mark.asyncio
    async def test_save_extracted_workflow_code_error(self, service, mock_agentic_entity):
        """Test extracted workflow code saving with error."""
        # Mock entity service to raise an exception
        service.entity_service.get_item = AsyncMock(side_effect=Exception("Save error"))

        result = await service.save_extracted_workflow_code(
            "tech_id", mock_agentic_entity,
            transition="test_transition"
        )

        assert "Error saving extracted workflow code" in result
        assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_convert_diagram_to_dataset_success(self, service, mock_chat_entity):
        """Test successful diagram to dataset conversion."""
        # Mock the conversion function and file operations
        with patch('common.utils.batch_converter.convert_state_diagram_to_jsonl_dataset') as mock_convert, \
             patch('builtins.open', mock_open(read_data="test content")):
            result = await service.convert_diagram_to_dataset(
                "tech_id", mock_chat_entity,
                input_file_path="/path/to/input.txt",
                output_file_path="/path/to/output.jsonl"
            )

            assert result == "Diagram converted to dataset successfully"

    @pytest.mark.asyncio
    async def test_convert_diagram_to_dataset_error(self, service, mock_chat_entity):
        """Test diagram to dataset conversion with error."""
        # Mock the conversion function to raise an exception
        with patch('common.utils.batch_converter.convert_state_diagram_to_jsonl_dataset', side_effect=Exception("Conversion error")):
            result = await service.convert_diagram_to_dataset(
                "tech_id", mock_chat_entity,
                input_file_path="/path/to/input.txt",
                output_file_path="/path/to/output.jsonl"
            )

            assert "Error converting diagram to dataset" in result
            assert mock_chat_entity.failed is True


    @pytest.mark.asyncio
    async def test_convert_workflow_processed_dataset_to_json_error(self, service, mock_chat_entity):
        """Test workflow processed dataset to JSON conversion with error."""
        # Mock external dependencies to raise an exception
        with patch('common.utils.batch_parallel_code.build_workflow_from_jsonl', new_callable=AsyncMock, side_effect=Exception("JSON error")):
            result = await service.convert_workflow_processed_dataset_to_json(
                "tech_id", mock_chat_entity,
                input_file_path="/path/to/input.jsonl",
                output_file_path="/path/to/output.json"
            )

            assert "Error converting workflow dataset" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_convert_workflow_json_to_state_diagram_success(self, service, mock_chat_entity):
        """Test successful workflow JSON to state diagram conversion."""
        # Mock external dependencies
        mock_data = {
            "initial_state": "state1",
            "states": {
                "state1": {
                    "transitions": {
                        "event1": {"next": "state2", "action": {"config": {"type": "function"}}}
                    }
                },
                "state2": {
                    "transitions": {}
                }
            }
        }
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_data))), \
             patch('json.load', return_value=mock_data), \
             patch('common.workflow.workflow_to_state_diagram_converter.convert_to_mermaid', return_value="mermaid_diagram"):

            result = await service.convert_workflow_json_to_state_diagram(
                "tech_id", mock_chat_entity,
                input_file_path="/path/to/input.json"
            )

            # The function is actually working and generating the mermaid diagram
            assert "stateDiagram-v2" in result
            assert "state1 --> state2" in result

    @pytest.mark.asyncio
    async def test_convert_workflow_json_to_state_diagram_error(self, service, mock_chat_entity):
        """Test workflow JSON to state diagram conversion with error."""
        # Mock external dependencies to raise an exception
        with patch('builtins.open', side_effect=Exception("Diagram error")):
            result = await service.convert_workflow_json_to_state_diagram(
                "tech_id", mock_chat_entity,
                input_file_path="/path/to/input.json"
            )

            assert "Error converting workflow to diagram" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_convert_workflow_to_dto_success(self, service, mock_agentic_entity):
        """Test successful workflow to DTO conversion."""
        # Mock external dependencies
        with patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/workflow.json"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            service.workflow_helper_service.read_json = AsyncMock(return_value={"workflow": "data"})
            service.workflow_helper_service.order_states_in_fsm = AsyncMock(return_value={"ordered": "fsm"})
            service.workflow_converter_service.convert_workflow = AsyncMock(return_value={"dto": "data"})
            service.workflow_helper_service.persist_json = AsyncMock()

            result = await service.convert_workflow_to_dto(
                "tech_id", mock_agentic_entity,
                workflow_file_name="workflow.json",
                output_file_name="output.json"
            )

            assert result == "Successfully converted workflow config to cyoda dto"

    @pytest.mark.asyncio
    async def test_convert_workflow_to_dto_error(self, service, mock_agentic_entity):
        """Test workflow to DTO conversion with error."""
        # Mock external dependencies to raise an exception
        with patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/workflow.json"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            service.workflow_helper_service.read_json = AsyncMock(side_effect=Exception("DTO error"))

            result = await service.convert_workflow_to_dto(
                "tech_id", mock_agentic_entity,
                workflow_file_name="workflow.json",
                output_file_name="output.json"
            )

            assert result == "Error while converting workflow"

    @pytest.mark.asyncio
    async def test_workflow_operations_with_custom_params(self, service, mock_agentic_entity):
        """Test workflow operations with custom parameters."""
        # Mock external dependencies
        mock_file_content = '{"entity_models": [{"entity_model_name": "test", "workflow_function": {"name": "test_func"}}], "file_without_workflow": {"code": "test_code"}}'

        def mock_aiofiles_open(*args, **kwargs):
            mock_file = AsyncMock()
            mock_file.read = AsyncMock(return_value=mock_file_content)
            mock_file.__aenter__ = AsyncMock(return_value=mock_file)
            mock_file.__aexit__ = AsyncMock(return_value=None)
            return mock_file

        with patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/file.json"), \
             patch('aiofiles.open', side_effect=mock_aiofiles_open), \
             patch('common.utils.utils._save_file', new_callable=AsyncMock), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            service.entity_service.add_item = AsyncMock(return_value="edge_message_123")
            service.workflow_helper_service.launch_agentic_workflow = AsyncMock(return_value="child_tech_id")
            service.workflow_helper_service.launch_scheduled_workflow = AsyncMock(return_value="scheduled_id")

            result = await service.register_workflow_with_app(
                "tech_id", mock_agentic_entity,
                filename="test.json",
                routes_file="routes.py",
                custom_param="value",
                timeout=300
            )

            assert result == "Workflow registration completed successfully"

    @pytest.mark.asyncio
    async def test_validation_operations_sequence(self, service, mock_agentic_entity):
        """Test sequence of validation operations."""
        # Mock entity service for validation operations
        service.entity_service.get_item = AsyncMock(return_value="validation_result")

        # Mock validate_ai_result for design validation
        with patch('tools.workflow_management_service.validate_ai_result', return_value=(True, "Valid")):
            # Perform validation sequence
            design_result = await service.validate_workflow_design(
                "tech_id", mock_agentic_entity,
                transition="test_transition"
            )
            success_result = await service.has_workflow_code_validation_succeeded(
                "tech_id", mock_agentic_entity,
                transition="test_transition"
            )
            failed_result = await service.has_workflow_code_validation_failed(
                "tech_id", mock_agentic_entity,
                transition="test_transition"
            )

            assert design_result == "Valid"
            assert success_result is True
            assert failed_result is False

    @pytest.mark.asyncio
    async def test_conversion_operations_sequence(self, service, mock_chat_entity, mock_agentic_entity):
        """Test sequence of conversion operations."""
        # Mock external dependencies for all conversion operations
        with patch('common.utils.batch_converter.convert_state_diagram_to_jsonl_dataset'), \
             patch('common.utils.batch_parallel_code.build_workflow_from_jsonl', new_callable=AsyncMock, return_value="workflow_result"), \
             patch('common.utils.utils._save_file', new_callable=AsyncMock), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"), \
             patch('builtins.open', mock_open(read_data=json.dumps({"initial_state": "state1", "states": {"state1": {"transitions": {"event1": {"next": "state2"}}}, "state2": {"transitions": {}}}}))), \
             patch('json.load', return_value={"initial_state": "state1", "states": {"state1": {"transitions": {"event1": {"next": "state2"}}}, "state2": {"transitions": {}}}}), \
             patch('common.workflow.workflow_to_state_diagram_converter.convert_to_mermaid', return_value="mermaid_diagram"), \
             patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/workflow.json"):

            # Mock workflow helper service methods for DTO conversion
            service.workflow_helper_service.read_json = AsyncMock(return_value={"workflow": "data"})
            service.workflow_helper_service.order_states_in_fsm = AsyncMock(return_value={"ordered": "fsm"})
            service.workflow_converter_service.convert_workflow = AsyncMock(return_value={"dto": "data"})
            service.workflow_helper_service.persist_json = AsyncMock()

            # Perform conversion sequence
            dataset_result = await service.convert_diagram_to_dataset(
                "tech_id", mock_chat_entity,
                input_file_path="/path/to/input.txt",
                output_file_path="/path/to/output.jsonl"
            )
            json_result = await service.convert_workflow_processed_dataset_to_json(
                "tech_id", mock_chat_entity,
                input_file_path="/path/to/input.jsonl",
                output_file_path="/path/to/output.json"
            )
            diagram_result = await service.convert_workflow_json_to_state_diagram(
                "tech_id", mock_chat_entity,
                input_file_path="/path/to/input.json"
            )
            dto_result = await service.convert_workflow_to_dto(
                "tech_id", mock_agentic_entity,
                workflow_file_name="workflow.json",
                output_file_name="output.json"
            )

            assert dataset_result == "Diagram converted to dataset successfully"
            assert "Error converting workflow dataset" in json_result
            assert "stateDiagram-v2" in diagram_result
            assert dto_result == "Successfully converted workflow config to cyoda dto"

    @pytest.mark.asyncio
    async def test_launch_gen_app_workflows_success(self, service, mock_agentic_entity):
        """Test successful launch of gen app workflows."""
        # Mock directory listing to return Java entity files
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=True), \
             patch('os.listdir', return_value=['Pet.java', 'Cat.java', 'Dog.java', '.hidden', 'NotJava.txt']), \
             patch('os.path.isfile', return_value=True), \
             patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/entities"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            service.workflow_helper_service.launch_agentic_workflow = AsyncMock(return_value="child_tech_id")
            service.workflow_helper_service.launch_scheduled_workflow = AsyncMock(return_value="scheduled_id")

            result = await service.launch_gen_app_workflows(
                "tech_id", mock_agentic_entity,
                dir_name="src/main/java/com/java_template/application/entity",
                next_transition="update_routes_file"
            )

            assert result == "Workflow registration completed successfully"
            # Verify that 3 workflows were launched (Pet, Cat, Dog - excluding .hidden and NotJava.txt)
            assert service.workflow_helper_service.launch_agentic_workflow.call_count == 3
            assert len(mock_agentic_entity.scheduled_entities) == 1

    @pytest.mark.asyncio
    async def test_launch_gen_app_workflows_no_entities(self, service, mock_agentic_entity):
        """Test launch gen app workflows when no Java entities found."""
        # Mock directory listing to return no Java files
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=True), \
             patch('os.listdir', return_value=['NotJava.txt', '.hidden']), \
             patch('os.path.isfile', return_value=True), \
             patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/entities"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            result = await service.launch_gen_app_workflows(
                "tech_id", mock_agentic_entity,
                dir_name="src/main/java/com/java_template/application/entity",
                next_transition="update_routes_file"
            )

            assert "No Java entity files found in directory" in result

    @pytest.mark.asyncio
    async def test_launch_gen_app_workflows_directory_not_exists(self, service, mock_agentic_entity):
        """Test launch gen app workflows when directory doesn't exist."""
        # Mock directory to not exist
        with patch('os.path.exists', return_value=False), \
             patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/entities"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            result = await service.launch_gen_app_workflows(
                "tech_id", mock_agentic_entity,
                dir_name="src/main/java/com/java_template/application/entity",
                next_transition="update_routes_file"
            )

            assert "No Java entity files found in directory" in result

    @pytest.mark.asyncio
    async def test_launch_gen_app_workflows_missing_params(self, service, mock_agentic_entity):
        """Test launch gen app workflows with missing required parameters."""
        # Test missing dir_name
        result = await service.launch_gen_app_workflows(
            "tech_id", mock_agentic_entity,
            next_transition="update_routes_file"
        )
        assert "Missing required parameter" in result

        # Test missing next_transition
        result = await service.launch_gen_app_workflows(
            "tech_id", mock_agentic_entity,
            dir_name="src/main/java/com/java_template/application/entity"
        )
        assert "Missing required parameter" in result

    @pytest.mark.asyncio
    async def test_launch_gen_app_workflows_error(self, service, mock_agentic_entity):
        """Test launch gen app workflows with error during workflow launch."""
        # Mock directory operations to succeed but workflow launch to fail
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=True), \
             patch('os.listdir', return_value=['Pet.java']), \
             patch('os.path.isfile', return_value=True), \
             patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/entities"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            service.workflow_helper_service.launch_agentic_workflow = AsyncMock(side_effect=Exception("Workflow launch error"))

            result = await service.launch_gen_app_workflows(
                "tech_id", mock_agentic_entity,
                dir_name="src/main/java/com/java_template/application/entity",
                next_transition="update_routes_file"
            )

            assert "Error registering workflow" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_get_entity_names_from_directory_success(self, service, mock_agentic_entity):
        """Test successful entity name extraction from directory."""
        # Mock directory listing with various file types
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=True), \
             patch('os.listdir', return_value=['Pet.java', 'Cat.java', 'Dog.java', '.hidden.java', 'NotJava.txt', 'subdirectory']), \
             patch('os.path.isfile', side_effect=lambda path: not path.endswith('subdirectory')), \
             patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/entities"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            entities = await service._get_entity_names_from_directory(
                dir_name="src/main/java/com/java_template/application/entity",
                technical_id="tech_id",
                entity=mock_agentic_entity
            )

            # Should return sorted list of Java entity names (excluding hidden files and non-Java files)
            assert entities == ['Cat', 'Dog', 'Pet']

    @pytest.mark.asyncio
    async def test_get_entity_names_from_directory_empty(self, service, mock_agentic_entity):
        """Test entity name extraction from empty directory."""
        with patch('os.path.exists', return_value=True), \
             patch('os.path.isdir', return_value=True), \
             patch('os.listdir', return_value=[]), \
             patch('common.utils.utils.get_project_file_name', new_callable=AsyncMock, return_value="/path/to/entities"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            entities = await service._get_entity_names_from_directory(
                dir_name="src/main/java/com/java_template/application/entity",
                technical_id="tech_id",
                entity=mock_agentic_entity
            )

            assert entities == []

    def test_service_inheritance(self, service):
        """Test that service properly inherits from BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        assert isinstance(service, BaseWorkflowService)
        assert hasattr(service, 'logger')
        assert hasattr(service, '_handle_error')
