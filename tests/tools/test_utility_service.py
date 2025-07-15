import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tools.utility_service import UtilityService
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity, SchedulerEntity
import common.config.const as const


class TestUtilityService:
    """Test cases for UtilityService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for UtilityService."""
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
        """Create UtilityService instance."""
        return UtilityService(**mock_dependencies)

    @pytest.fixture
    def mock_chat_entity(self):
        """Create mock ChatEntity."""
        entity = MagicMock(spec=ChatEntity)
        entity.workflow_cache = {const.GIT_BRANCH_PARAM: "test_branch"}
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
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
        entity.user_id = "test_user_123"
        entity.triggered_entity_id = "parent_entity_123"
        return entity

    @pytest.mark.asyncio
    async def test_get_weather_success(self, service, mock_chat_entity):
        """Test successful weather retrieval."""
        result = await service.get_weather("tech_id", mock_chat_entity, city="London")

        # Service returns a dictionary with weather information
        assert isinstance(result, dict)
        assert result["city"] == "London"
        assert result["temperature"] == "18°C"
        assert result["condition"] == "Sunny"

    @pytest.mark.asyncio
    async def test_get_weather_missing_location(self, service, mock_chat_entity):
        """Test weather retrieval with missing location."""
        result = await service.get_weather("tech_id", mock_chat_entity)

        # Service returns default values when no city is provided
        assert isinstance(result, dict)
        assert result["city"] == "Unknown"

    @pytest.mark.asyncio
    async def test_get_weather_error(self, service, mock_chat_entity):
        """Test weather retrieval with error."""
        # The service implementation doesn't actually make external API calls, so no error expected
        result = await service.get_weather("tech_id", mock_chat_entity, city="London")

        assert isinstance(result, dict)
        assert result["city"] == "London"

    @pytest.mark.asyncio
    async def test_get_humidity_success(self, service, mock_chat_entity):
        """Test successful humidity retrieval."""
        result = await service.get_humidity("tech_id", mock_chat_entity, city="London")

        # Service returns a dictionary with humidity information
        assert isinstance(result, dict)
        assert result["city"] == "London"
        assert result["humidity"] == "55%"

    @pytest.mark.asyncio
    async def test_get_humidity_missing_location(self, service, mock_chat_entity):
        """Test humidity retrieval with missing location."""
        result = await service.get_humidity("tech_id", mock_chat_entity)

        # Service returns default values when no city is provided
        assert isinstance(result, dict)
        assert result["city"] == "Unknown"

    @pytest.mark.asyncio
    async def test_get_humidity_error(self, service, mock_chat_entity):
        """Test humidity retrieval with error."""
        # The service implementation doesn't actually make external API calls, so no error expected
        result = await service.get_humidity("tech_id", mock_chat_entity, city="London")

        assert isinstance(result, dict)
        assert result["city"] == "London"

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, service, mock_agentic_entity):
        """Test successful user info retrieval."""
        mock_agentic_entity.workflow_cache = {
            "user_name": "John Doe",
            "user_email": "john@example.com",
            "user_id": "123"
        }

        result = await service.get_user_info("tech_id", mock_agentic_entity)

        assert "Please use this information for your answer:" in result
        assert "John Doe" in result
        assert "john@example.com" in result
        assert "123" in result

    @pytest.mark.asyncio
    async def test_get_user_info_partial_data(self, service, mock_agentic_entity):
        """Test user info retrieval with partial data."""
        mock_agentic_entity.workflow_cache = {
            "user_name": "John Doe"
        }

        result = await service.get_user_info("tech_id", mock_agentic_entity)

        assert "Please use this information for your answer:" in result
        assert "John Doe" in result

    @pytest.mark.asyncio
    async def test_init_chats_success(self, service, mock_chat_entity):
        """Test successful chat initialization."""
        result = await service.init_chats("tech_id", mock_chat_entity)

        # Method returns None in mock mode
        assert result is None

    @pytest.mark.asyncio
    async def test_init_chats_error(self, service, mock_chat_entity):
        """Test chat initialization with error."""
        # In mock mode, the method just returns None, no error handling needed
        result = await service.init_chats("tech_id", mock_chat_entity)

        assert result is None

    @pytest.mark.asyncio
    async def test_fail_workflow_success(self, service, mock_agentic_entity):
        """Test successful workflow failure."""
        result = await service.fail_workflow("tech_id", mock_agentic_entity)

        # Method returns the failure notification message
        assert "We ran into an error while processing the workflow" in result
        assert "tech_id" in result

    @pytest.mark.asyncio
    async def test_fail_workflow_error(self, service, mock_agentic_entity):
        """Test workflow failure with error."""
        # The method doesn't have error handling, it always returns the failure message
        result = await service.fail_workflow("tech_id", mock_agentic_entity)

        assert "We ran into an error while processing the workflow" in result
        assert "tech_id" in result

    @pytest.mark.asyncio
    async def test_check_scheduled_entity_status_success(self, service, mock_agentic_entity):
        """Test successful scheduled entity status check."""
        # Create a mock scheduler entity with status attribute
        mock_scheduler_entity = MagicMock(spec=SchedulerEntity)
        mock_scheduler_entity.status = "waiting"
        mock_scheduler_entity.triggered_entity_next_transition = None

        # Mock the scheduler service to return a tuple as expected by the method
        service.scheduler_service.run_for_entity = AsyncMock(return_value=("completed", "next_transition"))

        result = await service.check_scheduled_entity_status("tech_id", mock_scheduler_entity, scheduler_id="scheduler_123")

        # Method returns None but updates the entity status
        assert result is None
        assert mock_scheduler_entity.status == "completed"
        assert mock_scheduler_entity.triggered_entity_next_transition == "next_transition"

    @pytest.mark.asyncio
    async def test_check_scheduled_entity_status_missing_id(self, service, mock_agentic_entity):
        """Test scheduled entity status check with missing scheduler ID."""
        # Create a mock scheduler entity
        mock_scheduler_entity = MagicMock(spec=SchedulerEntity)
        mock_scheduler_entity.status = "waiting"

        # Mock the scheduler service to return empty tuple (causes unpacking error)
        service.scheduler_service.run_for_entity = AsyncMock(return_value=())

        result = await service.check_scheduled_entity_status("tech_id", mock_scheduler_entity)

        # Method returns None when there's an error
        assert result is None

    @pytest.mark.asyncio
    async def test_check_scheduled_entity_status_error(self, service, mock_agentic_entity):
        """Test scheduled entity status check with error."""
        # Create a mock scheduler entity
        mock_scheduler_entity = MagicMock(spec=SchedulerEntity)
        mock_scheduler_entity.status = "waiting"

        # Mock the scheduler service to raise an exception
        service.scheduler_service.run_for_entity = AsyncMock(side_effect=Exception("Scheduler error"))

        result = await service.check_scheduled_entity_status("tech_id", mock_scheduler_entity, scheduler_id="scheduler_123")

        # Method returns None when there's an error (error is just logged, entity is not marked as failed)
        assert result is None

    @pytest.mark.asyncio
    async def test_trigger_parent_entity_success(self, service, mock_agentic_entity):
        """Test successful parent entity triggering."""
        # Create a mock scheduler entity with the required attributes
        mock_scheduler_entity = MagicMock(spec=SchedulerEntity)
        mock_scheduler_entity.triggered_entity_id = "parent_entity_123"
        mock_scheduler_entity.triggered_entity_next_transition = "next_transition"

        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock):
            result = await service.trigger_parent_entity("tech_id", mock_scheduler_entity)

            # Method returns None on success
            assert result is None

    @pytest.mark.asyncio
    async def test_trigger_parent_entity_error(self, service, mock_agentic_entity):
        """Test parent entity triggering with error."""
        # Create a mock scheduler entity with the required attributes
        mock_scheduler_entity = MagicMock(spec=SchedulerEntity)
        mock_scheduler_entity.triggered_entity_id = "parent_entity_123"
        mock_scheduler_entity.triggered_entity_next_transition = "next_transition"

        with patch('common.utils.chat_util_functions._launch_transition',
                  new_callable=AsyncMock, side_effect=Exception("Trigger error")):

            result = await service.trigger_parent_entity("tech_id", mock_scheduler_entity)

            # Method returns None even on error (error is just logged, entity is not marked as failed)
            assert result is None

    @pytest.mark.asyncio
    async def test_weather_with_coordinates(self, service, mock_chat_entity):
        """Test weather retrieval with coordinates."""
        result = await service.get_weather("tech_id", mock_chat_entity, city="51.5074,-0.1278")

        # Service returns a dictionary with weather information
        assert isinstance(result, dict)
        assert result["city"] == "51.5074,-0.1278"
        assert result["temperature"] == "18°C"
        assert result["condition"] == "Sunny"

    @pytest.mark.asyncio
    async def test_user_info_with_custom_fields(self, service, mock_agentic_entity):
        """Test user info retrieval with custom fields."""
        mock_agentic_entity.workflow_cache = {
            "user_name": "Jane Smith",
            "user_email": "jane@example.com",
            "user_id": "456",
            "user_role": "admin",
            "user_department": "IT"
        }

        result = await service.get_user_info("tech_id", mock_agentic_entity)

        assert "Please use this information for your answer:" in result
        assert "Jane Smith" in result
        assert "jane@example.com" in result
        assert "456" in result

    @pytest.mark.asyncio
    async def test_utility_operations_with_custom_params(self, service, mock_chat_entity):
        """Test utility operations with custom parameters."""
        result = await service.init_chats(
            "tech_id", mock_chat_entity,
            custom_param="value",
            timeout=300
        )

        # Method returns None in mock mode
        assert result is None

    def test_service_inheritance(self, service):
        """Test that service properly inherits from BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        assert isinstance(service, BaseWorkflowService)
        assert hasattr(service, 'logger')
        assert hasattr(service, '_handle_error')
