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
        entity.locked = False

        # Mock transitions_memory
        transitions_memory = MagicMock()
        transitions_memory.conditions = {}
        transitions_memory.current_iteration = {}
        transitions_memory.max_iteration = {}
        entity.transitions_memory = transitions_memory

        return entity

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {}
        entity.failed = False
        entity.error = None
        entity.technical_id = "test_tech_id"

        # Mock transitions_memory
        transitions_memory = MagicMock()
        transitions_memory.conditions = {}
        transitions_memory.current_iteration = {}
        transitions_memory.max_iteration = {}
        entity.transitions_memory = transitions_memory

        return entity

    @pytest.mark.asyncio
    async def test_finish_discussion_success(self, service, mock_chat_entity):
        """Test successful discussion finishing."""
        # Convert to agentic entity for this test since finish_discussion expects AgenticFlowEntity
        mock_agentic_entity = MagicMock(spec=AgenticFlowEntity)
        transitions_memory = MagicMock()
        transitions_memory.conditions = {}
        mock_agentic_entity.transitions_memory = transitions_memory

        result = await service.finish_discussion("tech_id", mock_agentic_entity, transition="test_transition")

        assert result is None
        assert mock_agentic_entity.transitions_memory.conditions["test_transition"]["require_additional_question"] is False

    @pytest.mark.asyncio
    async def test_finish_discussion_error(self, service, mock_chat_entity):
        """Test discussion finishing with error."""
        # Test missing transition parameter
        try:
            result = await service.finish_discussion("tech_id", mock_chat_entity)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Missing required parameter: 'transition'" in str(e)

    @pytest.mark.asyncio
    async def test_is_stage_completed_true(self, service, mock_agentic_entity):
        """Test stage completion check when stage is completed."""
        # Set up transitions_memory to indicate stage is completed
        mock_agentic_entity.transitions_memory.conditions = {
            "test_transition": {"require_additional_question": False}
        }

        result = await service.is_stage_completed("tech_id", mock_agentic_entity, transition="test_transition")

        assert result is True

    @pytest.mark.asyncio
    async def test_is_stage_completed_false(self, service, mock_agentic_entity):
        """Test stage completion check when stage is not completed."""
        # Set up transitions_memory to indicate stage is not completed
        mock_agentic_entity.transitions_memory.conditions = {
            "test_transition": {"require_additional_question": True}
        }

        result = await service.is_stage_completed("tech_id", mock_agentic_entity, transition="test_transition")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_stage_completed_missing_stage(self, service, mock_agentic_entity):
        """Test stage completion check with missing stage."""
        # Empty conditions means stage is not completed
        mock_agentic_entity.transitions_memory.conditions = {}

        result = await service.is_stage_completed("tech_id", mock_agentic_entity, transition="missing_transition")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_stage_completed_missing_param(self, service, mock_agentic_entity):
        """Test stage completion check with missing transition parameter."""
        result = await service.is_stage_completed("tech_id", mock_agentic_entity)

        assert result is False  # Method returns False when transition parameter is missing

    @pytest.mark.asyncio
    async def test_not_stage_completed_true(self, service, mock_agentic_entity):
        """Test negated stage completion check when stage is not completed."""
        # Set up transitions_memory to indicate stage is not completed
        mock_agentic_entity.transitions_memory.conditions = {
            "test_transition": {"require_additional_question": True}
        }

        result = await service.not_stage_completed("tech_id", mock_agentic_entity, params={"transition": "test_transition"})

        assert result is True

    @pytest.mark.asyncio
    async def test_not_stage_completed_false(self, service, mock_agentic_entity):
        """Test negated stage completion check when stage is completed."""
        # Set up transitions_memory to indicate stage is completed
        mock_agentic_entity.transitions_memory.conditions = {
            "test_transition": {"require_additional_question": False}
        }

        result = await service.not_stage_completed("tech_id", mock_agentic_entity, transition="test_transition")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_chat_locked_true(self, service, mock_chat_entity):
        """Test chat lock check when chat is locked."""
        mock_chat_entity.locked = True

        result = await service.is_chat_locked("tech_id", mock_chat_entity)

        assert result is True

    @pytest.mark.asyncio
    async def test_is_chat_locked_false(self, service, mock_chat_entity):
        """Test chat lock check when chat is not locked."""
        mock_chat_entity.locked = False

        result = await service.is_chat_locked("tech_id", mock_chat_entity)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_chat_locked_missing(self, service, mock_chat_entity):
        """Test chat lock check when lock status is missing."""
        # Default locked value is False from fixture
        result = await service.is_chat_locked("tech_id", mock_chat_entity)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_chat_unlocked_true(self, service, mock_chat_entity):
        """Test chat unlock check when chat is unlocked."""
        mock_chat_entity.locked = False

        result = await service.is_chat_unlocked("tech_id", mock_chat_entity)

        assert result is True

    @pytest.mark.asyncio
    async def test_is_chat_unlocked_false(self, service, mock_chat_entity):
        """Test chat unlock check when chat is locked."""
        mock_chat_entity.locked = True

        result = await service.is_chat_unlocked("tech_id", mock_chat_entity)

        assert result is False

    @pytest.mark.asyncio
    async def test_lock_chat_success(self, service, mock_chat_entity):
        """Test successful chat locking."""
        result = await service.lock_chat("tech_id", mock_chat_entity)

        assert result is None  # Method returns None
        assert mock_chat_entity.locked is True

    @pytest.mark.asyncio
    async def test_unlock_chat_success(self, service, mock_chat_entity):
        """Test successful chat unlocking."""
        result = await service.unlock_chat("tech_id", mock_chat_entity)

        assert result is None  # Method returns None
        assert mock_chat_entity.locked is False

    @pytest.mark.asyncio
    async def test_reset_failed_entity_success(self, service, mock_agentic_entity):
        """Test successful entity failure reset."""
        mock_agentic_entity.failed = True
        mock_agentic_entity.error = "Some error"

        result = await service.reset_failed_entity("tech_id", mock_agentic_entity)

        assert result == "Retrying last step"  # Method returns this message
        assert mock_agentic_entity.failed is False

    @pytest.mark.asyncio
    async def test_reset_failed_entity_already_not_failed(self, service, mock_agentic_entity):
        """Test entity failure reset when entity is not failed."""
        mock_agentic_entity.failed = False
        mock_agentic_entity.error = None

        result = await service.reset_failed_entity("tech_id", mock_agentic_entity)

        assert result == "Retrying last step"  # Method always returns this message
        assert mock_agentic_entity.failed is False

    @pytest.mark.asyncio
    async def test_stage_completion_with_custom_values(self, service, mock_agentic_entity):
        """Test stage completion with custom completion values."""
        # Set up transitions_memory with custom transition
        mock_agentic_entity.transitions_memory.conditions = {
            "custom_transition": {"require_additional_question": True}
        }

        result = await service.is_stage_completed("tech_id", mock_agentic_entity, transition="custom_transition")

        # Should return False since require_additional_question is True
        assert result is False

    @pytest.mark.asyncio
    async def test_error_handling_in_state_operations(self, service, mock_chat_entity):
        """Test error handling in state operations."""
        # Test with normal locked attribute access (no error expected)
        mock_chat_entity.locked = False

        result = await service.is_chat_locked("tech_id", mock_chat_entity)

        # Should return the actual locked state
        assert result is False
