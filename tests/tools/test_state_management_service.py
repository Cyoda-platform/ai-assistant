import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tools.state_management_service import StateManagementService
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
import common.config.const as const


class TestStateManagementService:
    """Test cases for StateManagementService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for StateManagementService."""
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
        """Create StateManagementService instance."""
        return StateManagementService(**mock_dependencies)

    @pytest.fixture
    def mock_chat_entity(self):
        """Create mock ChatEntity."""
        entity = MagicMock(spec=ChatEntity)
        entity.workflow_cache = {}
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
        return entity

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {}
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"
        return entity

    @pytest.mark.asyncio
    async def test_finish_discussion_success(self, service, mock_chat_entity):
        """Test successful discussion finishing."""
        with patch('common.utils.chat_util_functions._launch_transition', new_callable=AsyncMock) as mock_transition:
            result = await service.finish_discussion("tech_id", mock_chat_entity)
            
            assert result == ""
            mock_transition.assert_called_once_with(
                entity=mock_chat_entity,
                transition_name=const.FINISH_DISCUSSION_TRANSITION
            )

    @pytest.mark.asyncio
    async def test_finish_discussion_error(self, service, mock_chat_entity):
        """Test discussion finishing with error."""
        with patch('common.utils.chat_util_functions._launch_transition', 
                  new_callable=AsyncMock, side_effect=Exception("Transition error")):
            
            result = await service.finish_discussion("tech_id", mock_chat_entity)
            
            assert "Error finishing discussion" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_is_stage_completed_true(self, service, mock_agentic_entity):
        """Test stage completion check when stage is completed."""
        mock_agentic_entity.workflow_cache = {"stage_name": "completed"}
        
        result = await service.is_stage_completed("tech_id", mock_agentic_entity, stage_name="stage_name")
        
        assert result == "True"

    @pytest.mark.asyncio
    async def test_is_stage_completed_false(self, service, mock_agentic_entity):
        """Test stage completion check when stage is not completed."""
        mock_agentic_entity.workflow_cache = {"stage_name": "in_progress"}
        
        result = await service.is_stage_completed("tech_id", mock_agentic_entity, stage_name="stage_name")
        
        assert result == "False"

    @pytest.mark.asyncio
    async def test_is_stage_completed_missing_stage(self, service, mock_agentic_entity):
        """Test stage completion check with missing stage."""
        result = await service.is_stage_completed("tech_id", mock_agentic_entity, stage_name="missing_stage")
        
        assert result == "False"

    @pytest.mark.asyncio
    async def test_is_stage_completed_missing_param(self, service, mock_agentic_entity):
        """Test stage completion check with missing stage_name parameter."""
        result = await service.is_stage_completed("tech_id", mock_agentic_entity)
        
        assert "Missing required parameters: stage_name" in result

    @pytest.mark.asyncio
    async def test_not_stage_completed_true(self, service, mock_agentic_entity):
        """Test negated stage completion check when stage is not completed."""
        mock_agentic_entity.workflow_cache = {"stage_name": "in_progress"}
        
        result = await service.not_stage_completed("tech_id", mock_agentic_entity, stage_name="stage_name")
        
        assert result == "True"

    @pytest.mark.asyncio
    async def test_not_stage_completed_false(self, service, mock_agentic_entity):
        """Test negated stage completion check when stage is completed."""
        mock_agentic_entity.workflow_cache = {"stage_name": "completed"}
        
        result = await service.not_stage_completed("tech_id", mock_agentic_entity, stage_name="stage_name")
        
        assert result == "False"

    @pytest.mark.asyncio
    async def test_is_chat_locked_true(self, service, mock_chat_entity):
        """Test chat lock check when chat is locked."""
        mock_chat_entity.workflow_cache = {const.CHAT_LOCKED_PARAM: True}
        
        result = await service.is_chat_locked("tech_id", mock_chat_entity)
        
        assert result == "True"

    @pytest.mark.asyncio
    async def test_is_chat_locked_false(self, service, mock_chat_entity):
        """Test chat lock check when chat is not locked."""
        mock_chat_entity.workflow_cache = {const.CHAT_LOCKED_PARAM: False}
        
        result = await service.is_chat_locked("tech_id", mock_chat_entity)
        
        assert result == "False"

    @pytest.mark.asyncio
    async def test_is_chat_locked_missing(self, service, mock_chat_entity):
        """Test chat lock check when lock status is missing."""
        result = await service.is_chat_locked("tech_id", mock_chat_entity)
        
        assert result == "False"

    @pytest.mark.asyncio
    async def test_is_chat_unlocked_true(self, service, mock_chat_entity):
        """Test chat unlock check when chat is unlocked."""
        mock_chat_entity.workflow_cache = {const.CHAT_LOCKED_PARAM: False}
        
        result = await service.is_chat_unlocked("tech_id", mock_chat_entity)
        
        assert result == "True"

    @pytest.mark.asyncio
    async def test_is_chat_unlocked_false(self, service, mock_chat_entity):
        """Test chat unlock check when chat is locked."""
        mock_chat_entity.workflow_cache = {const.CHAT_LOCKED_PARAM: True}
        
        result = await service.is_chat_unlocked("tech_id", mock_chat_entity)
        
        assert result == "False"

    @pytest.mark.asyncio
    async def test_lock_chat_success(self, service, mock_chat_entity):
        """Test successful chat locking."""
        result = await service.lock_chat("tech_id", mock_chat_entity)
        
        assert result == ""
        assert mock_chat_entity.workflow_cache[const.CHAT_LOCKED_PARAM] is True

    @pytest.mark.asyncio
    async def test_unlock_chat_success(self, service, mock_chat_entity):
        """Test successful chat unlocking."""
        result = await service.unlock_chat("tech_id", mock_chat_entity)
        
        assert result == ""
        assert mock_chat_entity.workflow_cache[const.CHAT_LOCKED_PARAM] is False

    @pytest.mark.asyncio
    async def test_reset_failed_entity_success(self, service, mock_agentic_entity):
        """Test successful entity failure reset."""
        mock_agentic_entity.failed = True
        mock_agentic_entity.error = "Some error"
        
        result = await service.reset_failed_entity("tech_id", mock_agentic_entity)
        
        assert result == ""
        assert mock_agentic_entity.failed is False
        assert mock_agentic_entity.error is None

    @pytest.mark.asyncio
    async def test_reset_failed_entity_already_not_failed(self, service, mock_agentic_entity):
        """Test entity failure reset when entity is not failed."""
        mock_agentic_entity.failed = False
        mock_agentic_entity.error = None
        
        result = await service.reset_failed_entity("tech_id", mock_agentic_entity)
        
        assert result == ""
        assert mock_agentic_entity.failed is False
        assert mock_agentic_entity.error is None

    @pytest.mark.asyncio
    async def test_stage_completion_with_custom_values(self, service, mock_agentic_entity):
        """Test stage completion with custom completion values."""
        mock_agentic_entity.workflow_cache = {"custom_stage": "done"}
        
        result = await service.is_stage_completed("tech_id", mock_agentic_entity, stage_name="custom_stage")
        
        # Should return False since "done" != "completed"
        assert result == "False"

    @pytest.mark.asyncio
    async def test_error_handling_in_state_operations(self, service, mock_chat_entity):
        """Test error handling in state operations."""
        # Simulate an error by making workflow_cache raise an exception
        mock_chat_entity.workflow_cache = MagicMock()
        mock_chat_entity.workflow_cache.__getitem__.side_effect = Exception("Cache error")
        
        result = await service.is_chat_locked("tech_id", mock_chat_entity)
        
        # Should handle error gracefully and return False
        assert result == "False"
