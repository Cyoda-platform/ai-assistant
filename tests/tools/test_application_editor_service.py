import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tools.application_editor_service import ApplicationEditorService
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
import common.config.const as const


class TestApplicationEditorService:
    """Test cases for ApplicationEditorService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for ApplicationEditorService."""
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
        """Create ApplicationEditorService instance."""
        return ApplicationEditorService(**mock_dependencies)

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
    async def test_edit_existing_app_design_additional_feature_success(self, service, mock_chat_entity):
        """Test successful additional feature design editing."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition, \
             patch.object(service, 'get_entities_list', return_value=["User", "Product"]), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):
            
            result = await service.edit_existing_app_design_additional_feature(
                "tech_id", mock_chat_entity,
                user_request="Add new feature"
            )
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_chat_entity,
                transition_name=const.EDIT_EXISTING_APP_DESIGN_ADDITIONAL_FEATURE_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_edit_existing_app_design_additional_feature_error(self, service, mock_chat_entity):
        """Test additional feature design editing with error."""
        with patch('common.utils.chat_util_functions._launch_transition', 
                  new_callable=AsyncMock, side_effect=Exception("Edit error")):
            
            result = await service.edit_existing_app_design_additional_feature(
                "tech_id", mock_chat_entity,
                user_request="Add new feature"
            )
            
            assert "Error editing existing app design" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_edit_api_existing_app_success(self, service, mock_agentic_entity):
        """Test successful API editing for existing app."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            result = await service.edit_api_existing_app(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_agentic_entity,
                transition_name=const.EDIT_API_EXISTING_APP_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_edit_api_existing_app_error(self, service, mock_agentic_entity):
        """Test API editing with error."""
        with patch('common.utils.chat_util_functions._launch_transition', 
                  new_callable=AsyncMock, side_effect=Exception("API edit error")):
            
            result = await service.edit_api_existing_app(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )
            
            assert "Error editing API for existing app" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_edit_existing_workflow_success(self, service, mock_agentic_entity):
        """Test successful existing workflow editing."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            result = await service.edit_existing_workflow(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_agentic_entity,
                transition_name=const.EDIT_EXISTING_WORKFLOW_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_edit_existing_workflow_error(self, service, mock_agentic_entity):
        """Test existing workflow editing with error."""
        with patch('common.utils.chat_util_functions._launch_transition', 
                  new_callable=AsyncMock, side_effect=Exception("Workflow edit error")):
            
            result = await service.edit_existing_workflow(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )
            
            assert "Error editing existing workflow" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_edit_existing_processors_success(self, service, mock_agentic_entity):
        """Test successful existing processors editing."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            result = await service.edit_existing_processors("tech_id", mock_agentic_entity)
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_agentic_entity,
                transition_name=const.EDIT_EXISTING_PROCESSORS_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_edit_existing_processors_error(self, service, mock_agentic_entity):
        """Test existing processors editing with error."""
        with patch('common.utils.chat_util_functions._launch_transition', 
                  new_callable=AsyncMock, side_effect=Exception("Processors edit error")):
            
            result = await service.edit_existing_processors("tech_id", mock_agentic_entity)
            
            assert "Error editing existing processors" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_add_new_entity_for_existing_app_success(self, service, mock_agentic_entity):
        """Test successful new entity addition for existing app."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            result = await service.add_new_entity_for_existing_app("tech_id", mock_agentic_entity)
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_agentic_entity,
                transition_name=const.ADD_NEW_ENTITY_FOR_EXISTING_APP_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_add_new_entity_for_existing_app_error(self, service, mock_agentic_entity):
        """Test new entity addition with error."""
        with patch('common.utils.chat_util_functions._launch_transition', 
                  new_callable=AsyncMock, side_effect=Exception("Entity add error")):
            
            result = await service.add_new_entity_for_existing_app("tech_id", mock_agentic_entity)
            
            assert "Error adding new entity for existing app" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_add_new_workflow_success(self, service, mock_agentic_entity):
        """Test successful new workflow addition."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            result = await service.add_new_workflow("tech_id", mock_agentic_entity)
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_agentic_entity,
                transition_name=const.ADD_NEW_WORKFLOW_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_add_new_workflow_error(self, service, mock_agentic_entity):
        """Test new workflow addition with error."""
        with patch('common.utils.chat_util_functions._launch_transition', 
                  new_callable=AsyncMock, side_effect=Exception("Workflow add error")):
            
            result = await service.add_new_workflow("tech_id", mock_agentic_entity)
            
            assert "Error adding new workflow" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_edit_with_entities_description(self, service, mock_chat_entity):
        """Test editing with entities description generation."""
        mock_entities = ["User", "Product", "Order"]
        
        with patch.object(service, 'get_entities_list', return_value=mock_entities), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"), \
             patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock):
            
            result = await service.edit_existing_app_design_additional_feature("tech_id", mock_chat_entity)
            
            assert result == ""
            # Check that entities description is generated
            expected_description = "User, Product, Order"
            assert mock_chat_entity.workflow_cache["entities_description"] == expected_description

    @pytest.mark.asyncio
    async def test_edit_with_empty_entities_list(self, service, mock_chat_entity):
        """Test editing with empty entities list."""
        with patch.object(service, 'get_entities_list', return_value=[]), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"), \
             patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock):
            
            result = await service.edit_existing_app_design_additional_feature("tech_id", mock_chat_entity)
            
            assert result == ""
            assert mock_chat_entity.workflow_cache["entities_description"] == ""

    @pytest.mark.asyncio
    async def test_edit_with_custom_params(self, service, mock_agentic_entity):
        """Test editing with custom parameters."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            result = await service.edit_api_existing_app(
                "tech_id", mock_agentic_entity,
                custom_param="value",
                timeout=300
            )
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_agentic_entity,
                transition_name=const.EDIT_API_EXISTING_APP_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_edit_with_missing_git_branch(self, service, mock_agentic_entity):
        """Test editing with missing git branch."""
        mock_agentic_entity.workflow_cache = {}  # No git branch
        
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock):
            result = await service.edit_existing_workflow("tech_id", mock_agentic_entity)
            
            assert result == ""

    @pytest.mark.asyncio
    async def test_multiple_edit_operations_sequence(self, service, mock_agentic_entity):
        """Test sequence of multiple edit operations."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            # Perform multiple edit operations
            await service.edit_api_existing_app("tech_id", mock_agentic_entity)
            await service.edit_existing_workflow("tech_id", mock_agentic_entity)
            await service.edit_existing_processors("tech_id", mock_agentic_entity)
            
            # Should have called transition three times
            assert mock_transition.call_count == 3

    def test_service_inheritance(self, service):
        """Test that service properly inherits from BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        assert isinstance(service, BaseWorkflowService)
        assert hasattr(service, 'logger')
        assert hasattr(service, '_handle_error')
        assert hasattr(service, 'get_entities_list')
