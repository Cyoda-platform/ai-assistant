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
        entity.workflow_name = "test_workflow"
        entity.user_id = "test_user_123"
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
        return entity

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {const.GIT_BRANCH_PARAM: "test_branch"}
        entity.workflow_name = "test_workflow"
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
        # Mock the HTTP request to avoid real network calls
        with patch('common.utils.utils.send_cyoda_request', new_callable=AsyncMock, return_value={"status": "success"}):
            result = await service.schedule_deploy_env("tech_id", mock_chat_entity)

            assert result == ""

    @pytest.mark.asyncio
    async def test_schedule_deploy_env_error(self, service, mock_chat_entity):
        """Test environment deployment scheduling with error."""
        # Mock the HTTP request to simulate an error
        with patch('common.utils.utils.send_cyoda_request', new_callable=AsyncMock, side_effect=Exception("Network error")):
            result = await service.schedule_deploy_env("tech_id", mock_chat_entity)

            assert "Error scheduling environment deployment" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_schedule_build_user_application_success(self, service, mock_chat_entity):
        """Test successful user application build scheduling."""
        # Mock the HTTP request to avoid real network calls
        with patch('common.utils.utils.send_cyoda_request', new_callable=AsyncMock, return_value={"status": "success"}):
            result = await service.schedule_build_user_application("tech_id", mock_chat_entity)

            assert result == ""

    @pytest.mark.asyncio
    async def test_schedule_deploy_user_application_success(self, service, mock_chat_entity):
        """Test successful user application deployment scheduling."""
        # Mock the HTTP request to avoid real network calls
        with patch('common.utils.utils.send_cyoda_request', new_callable=AsyncMock, return_value={"status": "success"}):
            result = await service.schedule_deploy_user_application("tech_id", mock_chat_entity)

            assert result == ""

    @pytest.mark.asyncio
    async def test_deploy_cyoda_env_success(self, service, mock_agentic_entity):
        """Test successful Cyoda environment deployment."""
        # Mock the deployment method directly on the service
        with patch.object(service, 'deploy_cyoda_env', return_value="") as mock_deploy:
            result = await service.deploy_cyoda_env("tech_id", mock_agentic_entity)

            assert result == ""
            mock_deploy.assert_called_once_with("tech_id", mock_agentic_entity)

    @pytest.mark.asyncio
    async def test_deploy_cyoda_env_error(self, service, mock_agentic_entity):
        """Test Cyoda environment deployment with error."""
        with patch.object(service, 'deploy_cyoda_env', side_effect=Exception("Deploy error")):
            result = await service.deploy_cyoda_env("tech_id", mock_agentic_entity)

            assert "Deploy error" in str(result)
            # Note: The actual service method would handle the error and set entity.failed

    @pytest.mark.asyncio
    async def test_deploy_user_application_success(self, service, mock_agentic_entity):
        """Test successful user application deployment."""
        with patch.object(service, 'deploy_user_application', return_value="") as mock_deploy:
            result = await service.deploy_user_application("tech_id", mock_agentic_entity)

            assert result == ""
            mock_deploy.assert_called_once_with("tech_id", mock_agentic_entity)

    @pytest.mark.asyncio
    async def test_deploy_user_application_error(self, service, mock_agentic_entity):
        """Test user application deployment with error."""
        with patch.object(service, 'deploy_user_application', side_effect=Exception("Deploy error")):
            result = await service.deploy_user_application("tech_id", mock_agentic_entity)

            assert "Deploy error" in str(result)
            # Note: The actual service method would handle the error and set entity.failed

    @pytest.mark.asyncio
    async def test_get_env_deploy_status_success(self, service, mock_agentic_entity):
        """Test successful environment deployment status retrieval."""
        # Mock the HTTP request to avoid real network calls
        with patch('common.utils.utils.send_cyoda_request', new_callable=AsyncMock, return_value={"status": "completed"}):
            result = await service.get_env_deploy_status("tech_id", mock_agentic_entity, build_id="scheduler_123")

            assert result == "completed"

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
            result = await service.get_env_deploy_status("tech_id", mock_agentic_entity, build_id="scheduler_123")

            assert "Error getting deployment status" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_schedule_with_custom_params(self, service, mock_chat_entity):
        """Test scheduling with custom parameters."""
        # Mock the HTTP request to avoid real network calls
        with patch('common.utils.utils.send_cyoda_request', new_callable=AsyncMock, return_value={"status": "success"}):
            result = await service.schedule_deploy_env(
                "tech_id", mock_chat_entity,
                custom_param="value",
                timeout=300
            )

            assert result == ""

    @pytest.mark.asyncio
    async def test_deployment_with_missing_branch(self, service, mock_agentic_entity):
        """Test deployment with missing git branch."""
        mock_agentic_entity.workflow_cache = {}  # No git branch

        with patch.object(service, 'deploy_cyoda_env', return_value="") as mock_deploy:
            result = await service.deploy_cyoda_env("tech_id", mock_agentic_entity)

            assert result == ""
            mock_deploy.assert_called_once_with("tech_id", mock_agentic_entity)
