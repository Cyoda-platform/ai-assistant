import pytest
from unittest.mock import AsyncMock, MagicMock, patch
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
        entity.workflow_cache = {const.GIT_BRANCH_PARAM: "test_branch"}
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
        return entity

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {const.GIT_BRANCH_PARAM: "test_branch"}
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
        return entity

    @pytest.mark.asyncio
    async def test_register_workflow_with_app_success(self, service, mock_agentic_entity):
        """Test successful workflow registration with app."""
        service.workflow_helper_service.register_workflow_with_app.return_value = "Registration successful"
        
        result = await service.register_workflow_with_app("tech_id", mock_agentic_entity)
        
        assert result == "Registration successful"
        service.workflow_helper_service.register_workflow_with_app.assert_called_once_with(
            entity=mock_agentic_entity
        )

    @pytest.mark.asyncio
    async def test_register_workflow_with_app_error(self, service, mock_agentic_entity):
        """Test workflow registration with error."""
        service.workflow_helper_service.register_workflow_with_app.side_effect = Exception("Registration error")
        
        result = await service.register_workflow_with_app("tech_id", mock_agentic_entity)
        
        assert "Error registering workflow with app" in result
        assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_validate_workflow_design_success(self, service, mock_agentic_entity):
        """Test successful workflow design validation."""
        service.workflow_helper_service.validate_workflow_design.return_value = "Validation passed"
        
        result = await service.validate_workflow_design("tech_id", mock_agentic_entity)
        
        assert result == "Validation passed"
        service.workflow_helper_service.validate_workflow_design.assert_called_once_with(
            entity=mock_agentic_entity
        )

    @pytest.mark.asyncio
    async def test_validate_workflow_design_error(self, service, mock_agentic_entity):
        """Test workflow design validation with error."""
        service.workflow_helper_service.validate_workflow_design.side_effect = Exception("Validation error")
        
        result = await service.validate_workflow_design("tech_id", mock_agentic_entity)
        
        assert "Error validating workflow design" in result
        assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_has_workflow_code_validation_succeeded_true(self, service, mock_agentic_entity):
        """Test workflow code validation success check when succeeded."""
        service.workflow_helper_service.has_workflow_code_validation_succeeded.return_value = True
        
        result = await service.has_workflow_code_validation_succeeded("tech_id", mock_agentic_entity)
        
        assert result == "True"

    @pytest.mark.asyncio
    async def test_has_workflow_code_validation_succeeded_false(self, service, mock_agentic_entity):
        """Test workflow code validation success check when failed."""
        service.workflow_helper_service.has_workflow_code_validation_succeeded.return_value = False
        
        result = await service.has_workflow_code_validation_succeeded("tech_id", mock_agentic_entity)
        
        assert result == "False"

    @pytest.mark.asyncio
    async def test_has_workflow_code_validation_succeeded_error(self, service, mock_agentic_entity):
        """Test workflow code validation success check with error."""
        service.workflow_helper_service.has_workflow_code_validation_succeeded.side_effect = Exception("Check error")
        
        result = await service.has_workflow_code_validation_succeeded("tech_id", mock_agentic_entity)
        
        assert "Error checking workflow code validation success" in result
        assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_has_workflow_code_validation_failed_true(self, service, mock_agentic_entity):
        """Test workflow code validation failure check when failed."""
        service.workflow_helper_service.has_workflow_code_validation_failed.return_value = True
        
        result = await service.has_workflow_code_validation_failed("tech_id", mock_agentic_entity)
        
        assert result == "True"

    @pytest.mark.asyncio
    async def test_has_workflow_code_validation_failed_false(self, service, mock_agentic_entity):
        """Test workflow code validation failure check when succeeded."""
        service.workflow_helper_service.has_workflow_code_validation_failed.return_value = False
        
        result = await service.has_workflow_code_validation_failed("tech_id", mock_agentic_entity)
        
        assert result == "False"

    @pytest.mark.asyncio
    async def test_save_extracted_workflow_code_success(self, service, mock_agentic_entity):
        """Test successful extracted workflow code saving."""
        service.workflow_helper_service.save_extracted_workflow_code.return_value = "Code saved successfully"
        
        result = await service.save_extracted_workflow_code("tech_id", mock_agentic_entity)
        
        assert result == "Code saved successfully"
        service.workflow_helper_service.save_extracted_workflow_code.assert_called_once_with(
            entity=mock_agentic_entity
        )

    @pytest.mark.asyncio
    async def test_save_extracted_workflow_code_error(self, service, mock_agentic_entity):
        """Test extracted workflow code saving with error."""
        service.workflow_helper_service.save_extracted_workflow_code.side_effect = Exception("Save error")
        
        result = await service.save_extracted_workflow_code("tech_id", mock_agentic_entity)
        
        assert "Error saving extracted workflow code" in result
        assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_convert_diagram_to_dataset_success(self, service, mock_agentic_entity):
        """Test successful diagram to dataset conversion."""
        service.workflow_converter_service.convert_diagram_to_dataset.return_value = "Dataset created"
        
        result = await service.convert_diagram_to_dataset("tech_id", mock_agentic_entity)
        
        assert result == "Dataset created"
        service.workflow_converter_service.convert_diagram_to_dataset.assert_called_once_with(
            entity=mock_agentic_entity
        )

    @pytest.mark.asyncio
    async def test_convert_diagram_to_dataset_error(self, service, mock_agentic_entity):
        """Test diagram to dataset conversion with error."""
        service.workflow_converter_service.convert_diagram_to_dataset.side_effect = Exception("Conversion error")
        
        result = await service.convert_diagram_to_dataset("tech_id", mock_agentic_entity)
        
        assert "Error converting diagram to dataset" in result
        assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_convert_workflow_processed_dataset_to_json_success(self, service, mock_agentic_entity):
        """Test successful workflow processed dataset to JSON conversion."""
        service.workflow_converter_service.convert_workflow_processed_dataset_to_json.return_value = "JSON created"
        
        result = await service.convert_workflow_processed_dataset_to_json("tech_id", mock_agentic_entity)
        
        assert result == "JSON created"
        service.workflow_converter_service.convert_workflow_processed_dataset_to_json.assert_called_once_with(
            entity=mock_agentic_entity
        )

    @pytest.mark.asyncio
    async def test_convert_workflow_processed_dataset_to_json_error(self, service, mock_agentic_entity):
        """Test workflow processed dataset to JSON conversion with error."""
        service.workflow_converter_service.convert_workflow_processed_dataset_to_json.side_effect = Exception("JSON error")
        
        result = await service.convert_workflow_processed_dataset_to_json("tech_id", mock_agentic_entity)
        
        assert "Error converting workflow processed dataset to JSON" in result
        assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_convert_workflow_json_to_state_diagram_success(self, service, mock_agentic_entity):
        """Test successful workflow JSON to state diagram conversion."""
        service.workflow_converter_service.convert_workflow_json_to_state_diagram.return_value = "Diagram created"
        
        result = await service.convert_workflow_json_to_state_diagram("tech_id", mock_agentic_entity)
        
        assert result == "Diagram created"
        service.workflow_converter_service.convert_workflow_json_to_state_diagram.assert_called_once_with(
            entity=mock_agentic_entity
        )

    @pytest.mark.asyncio
    async def test_convert_workflow_json_to_state_diagram_error(self, service, mock_agentic_entity):
        """Test workflow JSON to state diagram conversion with error."""
        service.workflow_converter_service.convert_workflow_json_to_state_diagram.side_effect = Exception("Diagram error")
        
        result = await service.convert_workflow_json_to_state_diagram("tech_id", mock_agentic_entity)
        
        assert "Error converting workflow JSON to state diagram" in result
        assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_convert_workflow_to_dto_success(self, service, mock_agentic_entity):
        """Test successful workflow to DTO conversion."""
        service.workflow_converter_service.convert_workflow_to_dto.return_value = "DTO created"
        
        result = await service.convert_workflow_to_dto("tech_id", mock_agentic_entity)
        
        assert result == "DTO created"
        service.workflow_converter_service.convert_workflow_to_dto.assert_called_once_with(
            entity=mock_agentic_entity
        )

    @pytest.mark.asyncio
    async def test_convert_workflow_to_dto_error(self, service, mock_agentic_entity):
        """Test workflow to DTO conversion with error."""
        service.workflow_converter_service.convert_workflow_to_dto.side_effect = Exception("DTO error")
        
        result = await service.convert_workflow_to_dto("tech_id", mock_agentic_entity)
        
        assert "Error converting workflow to DTO" in result
        assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_workflow_operations_with_custom_params(self, service, mock_agentic_entity):
        """Test workflow operations with custom parameters."""
        service.workflow_helper_service.register_workflow_with_app.return_value = "Success"
        
        result = await service.register_workflow_with_app(
            "tech_id", mock_agentic_entity,
            custom_param="value",
            timeout=300
        )
        
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_validation_operations_sequence(self, service, mock_agentic_entity):
        """Test sequence of validation operations."""
        service.workflow_helper_service.validate_workflow_design.return_value = "Valid"
        service.workflow_helper_service.has_workflow_code_validation_succeeded.return_value = True
        service.workflow_helper_service.has_workflow_code_validation_failed.return_value = False
        
        # Perform validation sequence
        design_result = await service.validate_workflow_design("tech_id", mock_agentic_entity)
        success_result = await service.has_workflow_code_validation_succeeded("tech_id", mock_agentic_entity)
        failed_result = await service.has_workflow_code_validation_failed("tech_id", mock_agentic_entity)
        
        assert design_result == "Valid"
        assert success_result == "True"
        assert failed_result == "False"

    @pytest.mark.asyncio
    async def test_conversion_operations_sequence(self, service, mock_agentic_entity):
        """Test sequence of conversion operations."""
        service.workflow_converter_service.convert_diagram_to_dataset.return_value = "Dataset"
        service.workflow_converter_service.convert_workflow_processed_dataset_to_json.return_value = "JSON"
        service.workflow_converter_service.convert_workflow_json_to_state_diagram.return_value = "Diagram"
        service.workflow_converter_service.convert_workflow_to_dto.return_value = "DTO"
        
        # Perform conversion sequence
        dataset_result = await service.convert_diagram_to_dataset("tech_id", mock_agentic_entity)
        json_result = await service.convert_workflow_processed_dataset_to_json("tech_id", mock_agentic_entity)
        diagram_result = await service.convert_workflow_json_to_state_diagram("tech_id", mock_agentic_entity)
        dto_result = await service.convert_workflow_to_dto("tech_id", mock_agentic_entity)
        
        assert dataset_result == "Dataset"
        assert json_result == "JSON"
        assert diagram_result == "Diagram"
        assert dto_result == "DTO"

    def test_service_inheritance(self, service):
        """Test that service properly inherits from BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        assert isinstance(service, BaseWorkflowService)
        assert hasattr(service, 'logger')
        assert hasattr(service, '_handle_error')
