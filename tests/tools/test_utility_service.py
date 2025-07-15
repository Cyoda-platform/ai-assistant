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
    async def test_get_weather_success(self, service, mock_chat_entity):
        """Test successful weather retrieval."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "current": {
                    "temperature_2m": 25.5,
                    "weather_code": 0
                }
            }
            mock_get.return_value = mock_response
            
            result = await service.get_weather("tech_id", mock_chat_entity, location="London")
            
            assert "25.5°C" in result
            assert "Clear sky" in result

    @pytest.mark.asyncio
    async def test_get_weather_missing_location(self, service, mock_chat_entity):
        """Test weather retrieval with missing location."""
        result = await service.get_weather("tech_id", mock_chat_entity)
        
        assert "Missing required parameters: location" in result

    @pytest.mark.asyncio
    async def test_get_weather_error(self, service, mock_chat_entity):
        """Test weather retrieval with error."""
        with patch('requests.get', side_effect=Exception("Weather API error")):
            result = await service.get_weather("tech_id", mock_chat_entity, location="London")
            
            assert "Error getting weather" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_get_humidity_success(self, service, mock_chat_entity):
        """Test successful humidity retrieval."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "current": {
                    "relative_humidity_2m": 65
                }
            }
            mock_get.return_value = mock_response
            
            result = await service.get_humidity("tech_id", mock_chat_entity, location="London")
            
            assert "65%" in result

    @pytest.mark.asyncio
    async def test_get_humidity_missing_location(self, service, mock_chat_entity):
        """Test humidity retrieval with missing location."""
        result = await service.get_humidity("tech_id", mock_chat_entity)
        
        assert "Missing required parameters: location" in result

    @pytest.mark.asyncio
    async def test_get_humidity_error(self, service, mock_chat_entity):
        """Test humidity retrieval with error."""
        with patch('requests.get', side_effect=Exception("Humidity API error")):
            result = await service.get_humidity("tech_id", mock_chat_entity, location="London")
            
            assert "Error getting humidity" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, service, mock_chat_entity):
        """Test successful user info retrieval."""
        mock_chat_entity.workflow_cache = {
            "user_name": "John Doe",
            "user_email": "john@example.com",
            "user_id": "123"
        }
        
        result = await service.get_user_info("tech_id", mock_chat_entity)
        
        assert "John Doe" in result
        assert "john@example.com" in result
        assert "123" in result

    @pytest.mark.asyncio
    async def test_get_user_info_partial_data(self, service, mock_chat_entity):
        """Test user info retrieval with partial data."""
        mock_chat_entity.workflow_cache = {
            "user_name": "John Doe"
        }
        
        result = await service.get_user_info("tech_id", mock_chat_entity)
        
        assert "John Doe" in result
        assert "Not available" in result  # For missing fields

    @pytest.mark.asyncio
    async def test_init_chats_success(self, service, mock_chat_entity):
        """Test successful chat initialization."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            result = await service.init_chats("tech_id", mock_chat_entity)
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_chat_entity,
                transition_name=const.INIT_CHATS_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_init_chats_error(self, service, mock_chat_entity):
        """Test chat initialization with error."""
        with patch('common.utils.chat_util_functions._launch_transition', 
                  new_callable=AsyncMock, side_effect=Exception("Init error")):
            
            result = await service.init_chats("tech_id", mock_chat_entity)
            
            assert "Error initializing chats" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_fail_workflow_success(self, service, mock_agentic_entity):
        """Test successful workflow failure."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            result = await service.fail_workflow("tech_id", mock_agentic_entity)
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_agentic_entity,
                transition_name=const.FAIL_WORKFLOW_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_fail_workflow_error(self, service, mock_agentic_entity):
        """Test workflow failure with error."""
        with patch('common.utils.chat_util_functions._launch_transition', 
                  new_callable=AsyncMock, side_effect=Exception("Fail error")):
            
            result = await service.fail_workflow("tech_id", mock_agentic_entity)
            
            assert "Error failing workflow" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_check_scheduled_entity_status_success(self, service, mock_agentic_entity):
        """Test successful scheduled entity status check."""
        mock_agentic_entity.workflow_cache = {"scheduler_id": "scheduler_123"}
        
        mock_scheduler = MagicMock(spec=SchedulerEntity)
        mock_scheduler.status = "completed"
        service.scheduler_service.get_item.return_value = mock_scheduler
        
        result = await service.check_scheduled_entity_status("tech_id", mock_agentic_entity, scheduler_id="scheduler_123")
        
        assert result == "completed"

    @pytest.mark.asyncio
    async def test_check_scheduled_entity_status_missing_id(self, service, mock_agentic_entity):
        """Test scheduled entity status check with missing scheduler ID."""
        result = await service.check_scheduled_entity_status("tech_id", mock_agentic_entity)
        
        assert "Missing required parameters: scheduler_id" in result

    @pytest.mark.asyncio
    async def test_check_scheduled_entity_status_error(self, service, mock_agentic_entity):
        """Test scheduled entity status check with error."""
        service.scheduler_service.get_item.side_effect = Exception("Scheduler error")
        
        result = await service.check_scheduled_entity_status("tech_id", mock_agentic_entity, scheduler_id="scheduler_123")
        
        assert "Error checking scheduled entity status" in result
        assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_trigger_parent_entity_success(self, service, mock_agentic_entity):
        """Test successful parent entity triggering."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            result = await service.trigger_parent_entity("tech_id", mock_agentic_entity)
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_agentic_entity,
                transition_name=const.TRIGGER_PARENT_ENTITY_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_trigger_parent_entity_error(self, service, mock_agentic_entity):
        """Test parent entity triggering with error."""
        with patch('common.utils.chat_util_functions._launch_transition', 
                  new_callable=AsyncMock, side_effect=Exception("Trigger error")):
            
            result = await service.trigger_parent_entity("tech_id", mock_agentic_entity)
            
            assert "Error triggering parent entity" in result
            assert mock_agentic_entity.failed is True

    @pytest.mark.asyncio
    async def test_weather_with_coordinates(self, service, mock_chat_entity):
        """Test weather retrieval with coordinates."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "current": {
                    "temperature_2m": 20.0,
                    "weather_code": 1
                }
            }
            mock_get.return_value = mock_response
            
            result = await service.get_weather("tech_id", mock_chat_entity, location="51.5074,-0.1278")
            
            assert "20.0°C" in result

    @pytest.mark.asyncio
    async def test_user_info_with_custom_fields(self, service, mock_chat_entity):
        """Test user info retrieval with custom fields."""
        mock_chat_entity.workflow_cache = {
            "user_name": "Jane Smith",
            "user_email": "jane@example.com",
            "user_id": "456",
            "user_role": "admin",
            "user_department": "IT"
        }
        
        result = await service.get_user_info("tech_id", mock_chat_entity)
        
        assert "Jane Smith" in result
        assert "jane@example.com" in result
        assert "456" in result

    @pytest.mark.asyncio
    async def test_utility_operations_with_custom_params(self, service, mock_chat_entity):
        """Test utility operations with custom parameters."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock):
            result = await service.init_chats(
                "tech_id", mock_chat_entity,
                custom_param="value",
                timeout=300
            )
            
            assert result == ""

    def test_service_inheritance(self, service):
        """Test that service properly inherits from BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        assert isinstance(service, BaseWorkflowService)
        assert hasattr(service, 'logger')
        assert hasattr(service, '_handle_error')
