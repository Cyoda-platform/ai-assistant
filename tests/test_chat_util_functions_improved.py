"""
Test suite for the improved traverse_and_process function in chat_util_functions.py
Run with: python -m pytest tests/test_chat_util_functions_improved.py -v
"""

import pytest
import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

# Import actual classes
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity, FlowEdgeMessage
import common.config.const as const
from common.config.config import config
from common.utils.chat_util_functions import trigger_manual_transition

# Setup logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestImprovedTraverseAndProcess:
    """Test suite for the improved traverse_and_process function in chat_util_functions.py"""
    
    @pytest.fixture
    def mock_entity_service(self):
        """Create a mock entity service"""
        service = AsyncMock()
        return service
    
    @pytest.fixture
    def mock_auth_service(self):
        """Create a mock auth service"""
        return "mock_token"
    
    @pytest.fixture
    def unlocked_chat_entity(self):
        """Create an unlocked chat entity"""
        entity = ChatEntity(memory_id="test_memory_1")
        entity.technical_id = "unlocked_1"
        entity.current_state = "ready"
        entity.child_entities = []
        entity.locked = False
        entity.user_id = "test_user"
        entity.chat_flow.finished_flow = []
        return entity
    
    @pytest.fixture
    def locked_chat_entity_no_children(self):
        """Create a locked chat entity with no children"""
        entity = ChatEntity(memory_id="test_memory_2")
        entity.technical_id = "locked_leaf"
        entity.current_state = "locked_chat_processing"
        entity.child_entities = []
        entity.locked = True
        entity.user_id = "test_user"
        entity.chat_flow.finished_flow = []
        return entity
    
    @pytest.fixture
    def locked_chat_entity_with_children(self):
        """Create a locked chat entity with children"""
        entity = ChatEntity(memory_id="test_memory_3")
        entity.technical_id = "locked_parent"
        entity.current_state = "locked_chat_processing"
        entity.child_entities = ["child_1", "child_2"]
        entity.locked = True
        entity.user_id = "test_user"
        entity.chat_flow.finished_flow = []
        return entity
    
    @pytest.mark.asyncio
    async def test_unlocked_entity_processes_immediately(self, unlocked_chat_entity, mock_entity_service, mock_auth_service):
        """Test that unlocked entities are processed immediately"""
        with patch('common.utils.chat_util_functions._launch_transition', return_value=True) as mock_launch, \
             patch('common.utils.chat_util_functions.add_answer_to_finished_flow', return_value=("edge_123", 1234567890)) as mock_add_flow:
            
            edge_message_id, transitioned = await trigger_manual_transition(
                entity_service=mock_entity_service,
                chat=unlocked_chat_entity,
                answer="test answer",
                cyoda_auth_service=mock_auth_service,
                transition=const.TransitionKey.PROCESS_USER_INPUT.value
            )
            
            assert transitioned is True
            assert edge_message_id == "edge_123"
            # Entity service should not be called for unlocked entities (no children to retrieve)
            mock_entity_service.get_item.assert_not_called()
            mock_launch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_locked_leaf_entity_unlocks_and_processes(self, locked_chat_entity_no_children, mock_entity_service, mock_auth_service):
        """Test that locked leaf entities are unlocked and processed"""
        with patch('common.utils.chat_util_functions._launch_transition', return_value=True) as mock_launch, \
             patch('common.utils.chat_util_functions.add_answer_to_finished_flow', return_value=("edge_123", 1234567890)) as mock_add_flow:
            
            edge_message_id, transitioned = await trigger_manual_transition(
                entity_service=mock_entity_service,
                chat=locked_chat_entity_no_children,
                answer="test answer",
                cyoda_auth_service=mock_auth_service,
                transition=const.TransitionKey.PROCESS_USER_INPUT.value
            )
            
            assert transitioned is True
            assert edge_message_id == "edge_123"
            assert locked_chat_entity_no_children.locked is False
            # Should have called _launch_transition twice: once for unlock, once for process
            assert mock_launch.call_count == 2
            mock_entity_service.get_item.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_locked_entity_with_unlocked_child(self, locked_chat_entity_with_children, mock_entity_service, mock_auth_service):
        """Test that locked entity with unlocked child processes the child"""
        # Create unlocked child
        unlocked_child = ChatEntity(memory_id="child_memory_1")
        unlocked_child.technical_id = "child_2"  # Will be processed first (reversed order)
        unlocked_child.current_state = "ready"
        unlocked_child.child_entities = []
        unlocked_child.locked = False
        unlocked_child.user_id = "test_user"
        unlocked_child.chat_flow.finished_flow = []
        
        mock_entity_service.get_item.return_value = unlocked_child
        
        with patch('common.utils.chat_util_functions._launch_transition', return_value=True) as mock_launch, \
             patch('common.utils.chat_util_functions.add_answer_to_finished_flow', return_value=("edge_123", 1234567890)) as mock_add_flow:
            
            edge_message_id, transitioned = await trigger_manual_transition(
                entity_service=mock_entity_service,
                chat=locked_chat_entity_with_children,
                answer="test answer",
                cyoda_auth_service=mock_auth_service,
                transition=const.TransitionKey.PROCESS_USER_INPUT.value
            )
            
            assert transitioned is True
            assert edge_message_id == "edge_123"
            # Should have tried to get child_2 first (reversed order)
            assert mock_entity_service.get_item.call_count >= 1
            mock_launch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_entity_service_failure_with_retry(self, locked_chat_entity_with_children, mock_entity_service, mock_auth_service):
        """Test retry mechanism when entity service fails"""
        # Create unlocked child
        unlocked_child = ChatEntity(memory_id="child_memory_1")
        unlocked_child.technical_id = "child_1"
        unlocked_child.current_state = "ready"
        unlocked_child.child_entities = []
        unlocked_child.locked = False
        unlocked_child.user_id = "test_user"
        unlocked_child.chat_flow.finished_flow = []
        
        # Setup mock to fail twice then succeed
        mock_entity_service.get_item.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            unlocked_child
        ]
        
        with patch('common.utils.chat_util_functions._launch_transition', return_value=True) as mock_launch, \
             patch('common.utils.chat_util_functions.add_answer_to_finished_flow', return_value=("edge_123", 1234567890)) as mock_add_flow:
            
            edge_message_id, transitioned = await trigger_manual_transition(
                entity_service=mock_entity_service,
                chat=locked_chat_entity_with_children,
                answer="test answer",
                cyoda_auth_service=mock_auth_service,
                transition=const.TransitionKey.PROCESS_USER_INPUT.value
            )
            
            assert transitioned is True
            assert edge_message_id == "edge_123"
            # Should have retried 3 times for the first child
            assert mock_entity_service.get_item.call_count == 3
            mock_launch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_entity_service_permanent_failure(self, locked_chat_entity_with_children, mock_entity_service, mock_auth_service):
        """Test behavior when entity service permanently fails"""
        # Setup mock to always fail
        mock_entity_service.get_item.side_effect = Exception("Permanent failure")
        
        with patch('common.utils.chat_util_functions._launch_transition', return_value=True) as mock_launch, \
             patch('common.utils.chat_util_functions.add_answer_to_finished_flow', return_value=("edge_123", 1234567890)) as mock_add_flow:
            
            edge_message_id, transitioned = await trigger_manual_transition(
                entity_service=mock_entity_service,
                chat=locked_chat_entity_with_children,
                answer="test answer",
                cyoda_auth_service=mock_auth_service,
                transition=const.TransitionKey.PROCESS_USER_INPUT.value
            )
            
            assert transitioned is True  # Should unlock root when children can't be retrieved
            assert edge_message_id == "edge_123"
            assert locked_chat_entity_with_children.locked is False
            # Should have tried max_retries times for each child
            assert mock_entity_service.get_item.call_count == 6  # 3 retries * 2 children
            # Should have called _launch_transition twice: once for unlock, once for process
            assert mock_launch.call_count == 2
    
    @pytest.mark.asyncio
    async def test_invalid_entity_returned(self, locked_chat_entity_with_children, mock_entity_service, mock_auth_service):
        """Test handling of invalid entities returned by service"""
        # Setup mock to return invalid entity (no current_state)
        invalid_entity = MagicMock()
        invalid_entity.current_state = None
        
        mock_entity_service.get_item.return_value = invalid_entity
        
        with patch('common.utils.chat_util_functions._launch_transition', return_value=True) as mock_launch, \
             patch('common.utils.chat_util_functions.add_answer_to_finished_flow', return_value=("edge_123", 1234567890)) as mock_add_flow:
            
            edge_message_id, transitioned = await trigger_manual_transition(
                entity_service=mock_entity_service,
                chat=locked_chat_entity_with_children,
                answer="test answer",
                cyoda_auth_service=mock_auth_service,
                transition=const.TransitionKey.PROCESS_USER_INPUT.value
            )
            
            assert transitioned is True  # Should unlock root when children are invalid
            assert edge_message_id == "edge_123"
            assert locked_chat_entity_with_children.locked is False
            # Should have called _launch_transition twice: once for unlock, once for process
            assert mock_launch.call_count == 2
    
    @pytest.mark.asyncio
    async def test_nested_locked_hierarchy(self, mock_entity_service, mock_auth_service):
        """Test traversal through nested locked entity hierarchy"""
        # Create root entity
        root_entity = ChatEntity(memory_id="root_memory")
        root_entity.technical_id = "root"
        root_entity.current_state = "locked_chat_processing"
        root_entity.child_entities = ["locked_child"]
        root_entity.locked = True
        root_entity.user_id = "test_user"
        root_entity.chat_flow.finished_flow = []
        
        # Create locked child
        locked_child = ChatEntity(memory_id="child_memory")
        locked_child.technical_id = "locked_child"
        locked_child.current_state = "locked_chat_processing"
        locked_child.child_entities = ["unlocked_grandchild"]
        locked_child.locked = True
        locked_child.user_id = "test_user"
        locked_child.chat_flow.finished_flow = []
        
        # Create unlocked grandchild
        unlocked_grandchild = ChatEntity(memory_id="grandchild_memory")
        unlocked_grandchild.technical_id = "unlocked_grandchild"
        unlocked_grandchild.current_state = "ready"
        unlocked_grandchild.child_entities = []
        unlocked_grandchild.locked = False
        unlocked_grandchild.user_id = "test_user"
        unlocked_grandchild.chat_flow.finished_flow = []
        
        # Setup mock to return appropriate entities
        def mock_get_item(token, entity_model, entity_version, technical_id):
            if technical_id == "locked_child":
                return locked_child
            elif technical_id == "unlocked_grandchild":
                return unlocked_grandchild
            return None
        
        mock_entity_service.get_item.side_effect = mock_get_item
        
        with patch('common.utils.chat_util_functions._launch_transition', return_value=True) as mock_launch, \
             patch('common.utils.chat_util_functions.add_answer_to_finished_flow', return_value=("edge_123", 1234567890)) as mock_add_flow:
            
            edge_message_id, transitioned = await trigger_manual_transition(
                entity_service=mock_entity_service,
                chat=root_entity,
                answer="test answer",
                cyoda_auth_service=mock_auth_service,
                transition=const.TransitionKey.PROCESS_USER_INPUT.value
            )
            
            assert transitioned is True
            assert edge_message_id == "edge_123"
            # Should have retrieved both child and grandchild
            assert mock_entity_service.get_item.call_count == 2
            mock_launch.assert_called_once()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
