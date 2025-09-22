import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import List

import common.config.const as const
from entity.chat.chat import ChatEntity
from entity.model import ChatFlow, FlowEdgeMessage
from tools.application_builder_service import ApplicationBuilderService


class TestApplicationBuilderServiceFileCollection:
    """Test file edge message ID collection functionality in ApplicationBuilderService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for ApplicationBuilderService."""
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
        """Create ApplicationBuilderService instance with mocked dependencies."""
        service = ApplicationBuilderService(**mock_dependencies)
        service._validate_required_params = AsyncMock(return_value=(True, None))
        service._handle_error = MagicMock(return_value="Error handled")
        return service

    @pytest.fixture
    def chat_entity_with_files(self):
        """Create a ChatEntity with file attachments in chat history."""
        # Create messages with various file attachment formats
        message1 = FlowEdgeMessage(
            type="answer",
            edge_message_id="msg1",
            file_blob_ids=["file1"],
            publish=True
        )
        
        message2 = FlowEdgeMessage(
            type="answer", 
            edge_message_id="msg2",
            file_blob_ids=["file2", "file3"],
            publish=True
        )
        
        message3 = FlowEdgeMessage(
            type="answer",
            edge_message_id="msg3",
            publish=True
        )

        message4 = FlowEdgeMessage(
            type="answer",
            edge_message_id="msg4",
            file_blob_ids=["file4", "file5"],
            publish=True
        )
        
        # Message without files
        message5 = FlowEdgeMessage(
            type="answer",
            edge_message_id="msg5",
            publish=True
        )

        chat_flow = ChatFlow(
            current_flow=[message1, message2],
            finished_flow=[message3, message4, message5]
        )
        
        return ChatEntity(
            user_id="test_user",
            chat_flow=chat_flow,
            memory_id="mem1"
        )

    @pytest.fixture
    def chat_entity_no_files(self):
        """Create a ChatEntity without file attachments."""
        message1 = FlowEdgeMessage(
            type="answer",
            edge_message_id="msg1",
            publish=True
        )
        
        message2 = FlowEdgeMessage(
            type="question",
            edge_message_id="msg2",
            publish=True
        )

        chat_flow = ChatFlow(
            current_flow=[message1],
            finished_flow=[message2]
        )
        
        return ChatEntity(
            user_id="test_user",
            chat_flow=chat_flow,
            memory_id="mem1"
        )

    def test_extract_file_ids_from_message_single_file(self, service):
        """Test extracting file IDs from message with single file in file_blob_ids."""
        message = FlowEdgeMessage(
            type="answer",
            file_blob_ids=["single_file"],
            edge_message_id="msg1"
        )

        result = service._extract_file_ids_from_message(message)
        assert result == ["single_file"]

    def test_extract_file_ids_from_message_multiple_files(self, service):
        """Test extracting file IDs from message with multiple file_blob_ids."""
        message = FlowEdgeMessage(
            type="answer",
            file_blob_ids=["file1", "file2", "file3"],
            edge_message_id="msg1"
        )
        
        result = service._extract_file_ids_from_message(message)
        assert result == ["file1", "file2", "file3"]



    def test_extract_file_ids_from_message_multiple_files_only(self, service):
        """Test extracting file IDs from message with only file_blob_ids."""
        message = FlowEdgeMessage(
            type="answer",
            file_blob_ids=["file1", "file2"],
            edge_message_id="msg1"
        )

        result = service._extract_file_ids_from_message(message)
        assert result == ["file1", "file2"]

    def test_extract_file_ids_from_message_empty_file_blob_ids(self, service):
        """Test extracting file IDs from message with empty file_blob_ids."""
        message = FlowEdgeMessage(
            type="answer",
            file_blob_ids=[],
            edge_message_id="msg1"
        )

        result = service._extract_file_ids_from_message(message)
        assert result == []

    def test_extract_file_ids_from_message_no_files(self, service):
        """Test extracting file IDs from message without files."""
        message = FlowEdgeMessage(
            type="answer",
            edge_message_id="msg1"
        )
        
        result = service._extract_file_ids_from_message(message)
        assert result == []

    def test_collect_file_edge_message_ids_with_files(self, service, chat_entity_with_files):
        """Test collecting file edge message IDs from entity with files."""
        result = service._collect_file_edge_message_ids(chat_entity_with_files)
        
        # Expected files: file1, file2, file3, file4, file5 (no attachments since they don't exist in model)
        expected = ["file1", "file2", "file3", "file4", "file5"]
        assert result == expected

    def test_collect_file_edge_message_ids_no_files(self, service, chat_entity_no_files):
        """Test collecting file edge message IDs from entity without files."""
        result = service._collect_file_edge_message_ids(chat_entity_no_files)
        assert result == []

    def test_collect_file_edge_message_ids_duplicates_removed(self, service):
        """Test that duplicate file IDs are removed while preserving order."""
        message1 = FlowEdgeMessage(
            type="answer",
            file_blob_ids=["file1", "file2"],
            edge_message_id="msg1"
        )
        
        message2 = FlowEdgeMessage(
            type="answer", 
            file_blob_ids=["file2", "file3"],  # file2 is duplicate
            edge_message_id="msg2"
        )

        chat_flow = ChatFlow(
            current_flow=[message1],
            finished_flow=[message2]
        )
        
        entity = ChatEntity(
            user_id="test_user",
            chat_flow=chat_flow,
            memory_id="mem1"
        )
        
        result = service._collect_file_edge_message_ids(entity)
        # Should preserve order and remove duplicates
        assert result == ["file1", "file2", "file3"]

    def test_collect_file_edge_message_ids_empty_chat_flow(self, service):
        """Test collecting file IDs from entity with empty chat flow."""
        entity = ChatEntity(
            user_id="test_user",
            chat_flow=None,
            memory_id="mem1"
        )
        
        result = service._collect_file_edge_message_ids(entity)
        assert result == []

    @pytest.mark.asyncio
    async def test_build_general_application_includes_file_ids(self, service, chat_entity_with_files):
        """Test that build_general_application includes file edge message IDs in workflow cache."""
        service.workflow_helper_service.launch_agentic_workflow.return_value = "child_id_123"
        
        params = {
            "user_request": "Build an app",
            "programming_language": "python",
            "mode": "build"
        }
        
        result = await service.build_general_application(
            technical_id="test_id",
            entity=chat_entity_with_files,
            **params
        )
        
        # Verify workflow was launched with file IDs in cache
        service.workflow_helper_service.launch_agentic_workflow.assert_called_once()
        call_args = service.workflow_helper_service.launch_agentic_workflow.call_args
        workflow_cache = call_args.kwargs["workflow_cache"]
        
        expected_file_ids = ["file1", "file2", "file3", "file4", "file5"]
        assert "file_edge_message_ids" in workflow_cache
        assert workflow_cache["file_edge_message_ids"] == expected_file_ids
        
        assert "child_id_123" in result

    @pytest.mark.asyncio
    async def test_build_general_application_no_files_no_param(self, service, chat_entity_no_files):
        """Test that build_general_application doesn't add file_edge_message_ids param when no files."""
        service.workflow_helper_service.launch_agentic_workflow.return_value = "child_id_123"
        
        params = {
            "user_request": "Build an app",
            "programming_language": "python", 
            "mode": "build"
        }
        
        result = await service.build_general_application(
            technical_id="test_id",
            entity=chat_entity_no_files,
            **params
        )
        
        # Verify workflow was launched without file IDs in cache
        service.workflow_helper_service.launch_agentic_workflow.assert_called_once()
        call_args = service.workflow_helper_service.launch_agentic_workflow.call_args
        workflow_cache = call_args.kwargs["workflow_cache"]
        
        assert "file_edge_message_ids" not in workflow_cache
        assert "child_id_123" in result
