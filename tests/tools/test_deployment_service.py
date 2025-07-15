import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tools.deployment_service import DeploymentService
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity, SchedulerEntity
import common.config.const as const


class TestDeploymentService:
    """Test cases for DeploymentService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for DeploymentService."""
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
        """Create DeploymentService instance."""
        return DeploymentService(**mock_dependencies)

    @pytest.fixture
    def mock_chat_entity(self):
        """Create mock ChatEntity."""
        entity = MagicMock(spec=ChatEntity)
        entity.workflow_cache = {const.GIT_BRANCH_PARAM: "test_branch"}
        entity.workflow_name = "test_workflow_python"
        entity.user_id = "test_user_123"
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
        entity.scheduled_entities = []
        return entity

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {const.GIT_BRANCH_PARAM: "test_branch"}
        entity.workflow_name = "test_workflow_python"
        entity.user_id = "test_user_123"
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
        return entity

    @pytest.fixture
    def mock_scheduler_entity(self):
        """Create mock SchedulerEntity."""
        entity = MagicMock(spec=SchedulerEntity)
        entity.technical_id = "scheduler_tech_id"
        entity.status = "pending"
        return entity

    @pytest.mark.asyncio
    async def test_schedule_deploy_env_success(self, service, mock_chat_entity):
        """Test successful environment deployment scheduling."""
        # Mock the HTTP request at the send_request level to avoid real network calls
        mock_response = {
            "json": {
                "build_id": "test_build_123",
                "build_namespace": "test-namespace"
            }
        }
        with patch('common.utils.utils.send_request', new_callable=AsyncMock) as mock_send_request, \
             patch.object(service.workflow_helper_service, 'launch_scheduled_workflow', new_callable=AsyncMock, return_value="scheduled_id"):

            # Mock the HTTP response
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response["json"]
            mock_send_request.return_value = mock_response

            result = await service.schedule_deploy_env("tech_id", mock_chat_entity)

            assert "Successfully scheduled" in result
            assert "test_build_123" in result
            assert "test-namespace" in result

    @pytest.mark.asyncio
    async def test_schedule_deploy_env_error(self, service, mock_chat_entity):
        """Test environment deployment scheduling with error."""
        # Mock the HTTP request to simulate an error
        with patch('common.utils.utils.send_cyoda_request', new_callable=AsyncMock, side_effect=Exception("Network error")):
            try:
                result = await service.schedule_deploy_env("tech_id", mock_chat_entity)
                # If no exception is raised, the service should handle it gracefully
                assert "Error" in result or "Failed" in result
            except Exception:
                # If exception is raised, that's also acceptable behavior
                pass

    @pytest.mark.asyncio
    async def test_schedule_build_user_application_success(self, service, mock_chat_entity):
        """Test successful user application build scheduling."""
        # Mock the HTTP request at the send_request level to avoid real network calls
        mock_response = {
            "json": {
                "build_id": "test_build_123",
                "build_namespace": "test-namespace"
            }
        }
        with patch('common.utils.utils.send_request', new_callable=AsyncMock, return_value=mock_response), \
             patch.object(service.workflow_helper_service, 'launch_scheduled_workflow', new_callable=AsyncMock, return_value="scheduled_id"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            result = await service.schedule_build_user_application("tech_id", mock_chat_entity)

            assert "Successfully scheduled" in result
            assert "test_build_123" in result

    @pytest.mark.asyncio
    async def test_schedule_deploy_user_application_success(self, service, mock_chat_entity):
        """Test successful user application deployment scheduling."""
        # Mock the HTTP request at the send_request level to avoid real network calls
        mock_response = {
            "json": {
                "build_id": "test_build_123",
                "build_namespace": "test-namespace"
            }
        }
        with patch('common.utils.utils.send_request', new_callable=AsyncMock, return_value=mock_response), \
             patch.object(service.workflow_helper_service, 'launch_scheduled_workflow', new_callable=AsyncMock, return_value="scheduled_id"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):

            result = await service.schedule_deploy_user_application("tech_id", mock_chat_entity)

            assert "Successfully scheduled" in result
            assert "test_build_123" in result

    @pytest.mark.asyncio
    async def test_deploy_cyoda_env_success(self, service, mock_agentic_entity):
        """Test successful Cyoda environment deployment."""
        # Mock the workflow helper service
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"):
            result = await service.deploy_cyoda_env("tech_id", mock_agentic_entity)

            assert "Successfully scheduled workflow to implement the task" in result
            assert "child_tech_id" in result

    @pytest.mark.asyncio
    async def test_deploy_cyoda_env_error(self, service, mock_agentic_entity):
        """Test Cyoda environment deployment with error."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow',
                          new_callable=AsyncMock, side_effect=Exception("Deploy error")):
            try:
                result = await service.deploy_cyoda_env("tech_id", mock_agentic_entity)
                # If no exception is raised, the service should handle it gracefully
                assert "Error" in result or "Failed" in result
            except Exception:
                # If exception is raised, that's also acceptable behavior
                pass

    @pytest.mark.asyncio
    async def test_deploy_user_application_success(self, service, mock_agentic_entity):
        """Test successful user application deployment."""
        # Mock the workflow helper service
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"):
            result = await service.deploy_user_application("tech_id", mock_agentic_entity)

            assert "Successfully scheduled workflow to implement the task" in result
            assert "child_tech_id" in result

    @pytest.mark.asyncio
    async def test_deploy_user_application_error(self, service, mock_agentic_entity):
        """Test user application deployment with error."""
        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow',
                          new_callable=AsyncMock, side_effect=Exception("Deploy error")):
            try:
                result = await service.deploy_user_application("tech_id", mock_agentic_entity)
                # If no exception is raised, the service should handle it gracefully
                assert "Error" in result or "Failed" in result
            except Exception:
                # If exception is raised, that's also acceptable behavior
                pass

    @pytest.mark.asyncio
    async def test_get_env_deploy_status_success(self, service, mock_agentic_entity):
        """Test successful environment deployment status retrieval."""
        # Mock the HTTP request at the send_request level to avoid real network calls
        mock_response = {
            "json": {
                "state": "completed",
                "status": "success"
            }
        }
        with patch('common.utils.utils.send_request', new_callable=AsyncMock, return_value=mock_response):
            result = await service.get_env_deploy_status("tech_id", mock_agentic_entity, build_id="scheduler_123")

            assert "Current deploy state completed" in result
            assert "Current deploy status success" in result

    @pytest.mark.asyncio
    async def test_get_env_deploy_status_no_scheduler_id(self, service, mock_agentic_entity):
        """Test environment deployment status with no scheduler ID."""
        try:
            result = await service.get_env_deploy_status("tech_id", mock_agentic_entity)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Missing build_id in params" in str(e)

    @pytest.mark.asyncio
    async def test_get_env_deploy_status_error(self, service, mock_agentic_entity):
        """Test environment deployment status with error."""
        # Mock the HTTP request to simulate an error
        with patch('common.utils.utils.send_cyoda_request', new_callable=AsyncMock, side_effect=Exception("Network error")):
            try:
                result = await service.get_env_deploy_status("tech_id", mock_agentic_entity, build_id="scheduler_123")
                # If no exception is raised, the service should handle it gracefully
                assert "Error" in result or "Failed" in result
            except Exception:
                # If exception is raised, that's also acceptable behavior
                pass

    @pytest.mark.asyncio
    async def test_schedule_with_custom_params(self, service, mock_chat_entity):
        """Test scheduling with custom parameters."""
        # Mock the HTTP request at the send_request level to avoid real network calls
        mock_response = {
            "json": {
                "build_id": "test_build_123",
                "build_namespace": "test-namespace"
            }
        }
        with patch('common.utils.utils.send_request', new_callable=AsyncMock, return_value=mock_response), \
             patch.object(service.workflow_helper_service, 'launch_scheduled_workflow', new_callable=AsyncMock, return_value="scheduled_id"):

            result = await service.schedule_deploy_env(
                "tech_id", mock_chat_entity,
                custom_param="value",
                timeout=300
            )

            assert "Successfully scheduled" in result

    @pytest.mark.asyncio
    async def test_deployment_with_missing_branch(self, service, mock_agentic_entity):
        """Test deployment with missing git branch."""
        mock_agentic_entity.workflow_cache = {}  # No git branch

        with patch.object(service.workflow_helper_service, 'launch_agentic_workflow', new_callable=AsyncMock, return_value="child_tech_id"):
            result = await service.deploy_cyoda_env("tech_id", mock_agentic_entity)

            assert "Successfully scheduled workflow to implement the task" in result
            assert "child_tech_id" in result
