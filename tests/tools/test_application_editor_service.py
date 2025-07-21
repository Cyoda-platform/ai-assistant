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
        entity.workflow_name = "test_workflow_python"
        entity.user_id = "test_user_123"
        return entity

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {const.GIT_BRANCH_PARAM: "test_branch"}
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
        entity.workflow_name = "test_workflow_python"
        entity.user_id = "test_user_123"
        return entity

    @pytest.mark.asyncio
    async def test_edit_existing_app_design_additional_feature_success(self, service, mock_chat_entity):
        """Test successful additional feature design editing."""
        # Mock all external dependencies to avoid actual file operations
        with patch('common.utils.utils.clone_repo', new_callable=AsyncMock), \
             patch('common.utils.utils.read_file_util', new_callable=AsyncMock, return_value="test_api_content"), \
             patch.object(service, 'get_entities_list', new_callable=AsyncMock, return_value=["User", "Product"]), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"), \
             patch.object(service.entity_service, 'add_item', new_callable=AsyncMock, return_value="mock_id"), \
             patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"), \
             patch('common.utils.utils.set_upstream_tracking', new_callable=AsyncMock), \
             patch('common.utils.utils.git_pull', new_callable=AsyncMock, return_value=""):

            result = await service.edit_existing_app_design_additional_feature(
                "tech_id", mock_chat_entity,
                user_request="Add new feature"
            )

            assert "Successfully scheduled workflow for updating user application" in result
            assert "child_tech_id" in result

    @pytest.mark.asyncio
    async def test_edit_existing_app_design_additional_feature_error(self, service, mock_chat_entity):
        """Test additional feature design editing with error."""
        # Mock the workflow helper service to raise an exception to trigger error handling
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow',
                          new_callable=AsyncMock, side_effect=Exception("Edit error")), \
             patch('common.utils.utils.clone_repo', new_callable=AsyncMock), \
             patch('common.utils.utils.read_file_util', new_callable=AsyncMock, return_value="test_api_content"), \
             patch.object(service, 'get_entities_list', new_callable=AsyncMock, return_value=["User", "Product"]), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"), \
             patch.object(service.entity_service, 'add_item', new_callable=AsyncMock, return_value="mock_id"):

            result = await service.edit_existing_app_design_additional_feature(
                "tech_id", mock_chat_entity,
                user_request="Add new feature"
            )

            assert "Error editing application design" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_edit_api_existing_app_success(self, service, mock_agentic_entity):
        """Test successful API editing for existing app."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"):
            result = await service.edit_api_existing_app(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Successfully scheduled workflow to implement the task" in result
            assert "child_tech_id" in result

    @pytest.mark.asyncio
    async def test_edit_api_existing_app_error(self, service, mock_agentic_entity):
        """Test API editing with error."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow',
                          new_callable=AsyncMock, side_effect=Exception("API edit error")):

            result = await service.edit_api_existing_app(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Error editing API" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_edit_existing_workflow_success(self, service, mock_agentic_entity):
        """Test successful existing workflow editing."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"):
            result = await service.edit_existing_workflow(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Successfully scheduled workflow to implement the task" in result
            assert "child_tech_id" in result

    @pytest.mark.asyncio
    async def test_edit_existing_workflow_error(self, service, mock_agentic_entity):
        """Test existing workflow editing with error."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow',
                          new_callable=AsyncMock, side_effect=Exception("Workflow edit error")):

            result = await service.edit_existing_workflow(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Error editing workflow" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_edit_existing_processors_success(self, service, mock_agentic_entity):
        """Test successful existing processors editing."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"):
            result = await service.edit_existing_processors(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Successfully scheduled workflow to implement the task" in result
            assert "child_tech_id" in result

    @pytest.mark.asyncio
    async def test_edit_existing_processors_error(self, service, mock_agentic_entity):
        """Test existing processors editing with error."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow',
                          new_callable=AsyncMock, side_effect=Exception("Processors edit error")):

            result = await service.edit_existing_processors(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Error editing processors" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_add_new_entity_for_existing_app_success(self, service, mock_agentic_entity):
        """Test successful new entity addition for existing app."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"):
            result = await service.add_new_entity_for_existing_app(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Successfully scheduled workflow to implement the task" in result
            assert "child_tech_id" in result

    @pytest.mark.asyncio
    async def test_add_new_entity_for_existing_app_error(self, service, mock_agentic_entity):
        """Test new entity addition with error."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow',
                          new_callable=AsyncMock, side_effect=Exception("Entity add error")):

            result = await service.add_new_entity_for_existing_app(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Error adding new entity" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_add_new_workflow_success(self, service, mock_agentic_entity):
        """Test successful new workflow addition."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"):
            result = await service.add_new_workflow(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Successfully scheduled workflow to implement the task" in result
            assert "child_tech_id" in result

    @pytest.mark.asyncio
    async def test_add_new_workflow_error(self, service, mock_agentic_entity):
        """Test new workflow addition with error."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow',
                          new_callable=AsyncMock, side_effect=Exception("Workflow add error")):

            result = await service.add_new_workflow(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Error adding new workflow" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_edit_with_entities_description(self, service, mock_chat_entity):
        """Test editing with entities description generation."""
        mock_entities = ["User", "Product", "Order"]

        with patch.object(service, 'get_entities_list', new_callable=AsyncMock, return_value=mock_entities), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"), \
             patch('common.utils.utils.clone_repo', new_callable=AsyncMock), \
             patch('common.utils.utils.read_file_util', new_callable=AsyncMock, return_value="test_api_content"), \
             patch.object(service.entity_service, 'add_item', new_callable=AsyncMock, return_value="mock_id"), \
             patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"), \
             patch('common.utils.utils.set_upstream_tracking', new_callable=AsyncMock), \
             patch('common.utils.utils.git_pull', new_callable=AsyncMock, return_value=""):

            result = await service.edit_existing_app_design_additional_feature(
                "tech_id", mock_chat_entity,
                user_request="Add new feature"
            )

            assert "Successfully scheduled workflow for updating user application" in result

    @pytest.mark.asyncio
    async def test_edit_with_empty_entities_list(self, service, mock_chat_entity):
        """Test editing with empty entities list."""
        with patch.object(service, 'get_entities_list', new_callable=AsyncMock, return_value=[]), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"), \
             patch('common.utils.utils.clone_repo', new_callable=AsyncMock), \
             patch('common.utils.utils.read_file_util', new_callable=AsyncMock, return_value="test_api_content"), \
             patch.object(service.entity_service, 'add_item', new_callable=AsyncMock, return_value="mock_id"), \
             patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"), \
             patch('common.utils.utils.set_upstream_tracking', new_callable=AsyncMock), \
             patch('common.utils.utils.git_pull', new_callable=AsyncMock, return_value=""):

            result = await service.edit_existing_app_design_additional_feature(
                "tech_id", mock_chat_entity,
                user_request="Add new feature"
            )

            assert "Successfully scheduled workflow for updating user application" in result

    @pytest.mark.asyncio
    async def test_edit_with_custom_params(self, service, mock_agentic_entity):
        """Test editing with custom parameters."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"):
            result = await service.edit_api_existing_app(
                "tech_id", mock_agentic_entity,
                programming_language="python",
                custom_param="value",
                timeout=300
            )

            assert "Successfully scheduled workflow to implement the task" in result

    @pytest.mark.asyncio
    async def test_edit_with_missing_git_branch(self, service, mock_agentic_entity):
        """Test editing with missing git branch."""
        mock_agentic_entity.workflow_cache = {}  # No git branch

        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"):
            result = await service.edit_existing_workflow(
                "tech_id", mock_agentic_entity,
                programming_language="python"
            )

            assert "Successfully scheduled workflow to implement the task" in result

    @pytest.mark.asyncio
    async def test_multiple_edit_operations_sequence(self, service, mock_agentic_entity):
        """Test sequence of multiple edit operations."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id") as mock_workflow:
            # Perform multiple edit operations
            await service.edit_api_existing_app("tech_id", mock_agentic_entity, programming_language="python")
            await service.edit_existing_workflow("tech_id", mock_agentic_entity, programming_language="python")
            await service.edit_existing_processors("tech_id", mock_agentic_entity, programming_language="python")

            # Should have called workflow launch three times
            assert mock_workflow.call_count == 3

    def test_service_inheritance(self, service):
        """Test that service properly inherits from BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        assert isinstance(service, BaseWorkflowService)
        assert hasattr(service, 'logger')
        assert hasattr(service, '_handle_error')
        assert hasattr(service, 'get_entities_list')
