import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.chat_service import ChatService
from services.user_answer_validation_service import UserAnswerValidationService
from common.utils.chat_util_functions import trigger_manual_transition, add_answer_to_finished_flow
from entity.chat.chat import ChatEntity
from entity.model import ChatFlow, FlowEdgeMessage


class TestUserAnswerValidationIntegration:
    
    @pytest.fixture
    def mock_entity_service(self):
        service = AsyncMock()
        service.add_item.return_value = "mock_edge_id_123"
        return service
    
    @pytest.fixture
    def mock_cyoda_auth_service(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_data_service(self):
        service = MagicMock()
        service.get_entities_by_user_name = AsyncMock(return_value=[])
        service.get_entities_by_user_name_and_workflow_name = AsyncMock(return_value=[])
        return service
    
    @pytest.fixture
    def validation_service(self, mock_entity_service, mock_cyoda_auth_service):
        return UserAnswerValidationService(mock_entity_service, mock_cyoda_auth_service)
    
    @pytest.fixture
    def chat_service(self, mock_entity_service, mock_cyoda_auth_service, mock_data_service):
        ai_agent = MagicMock()
        chat_lock = MagicMock()
        return ChatService(mock_entity_service, mock_cyoda_auth_service, chat_lock, ai_agent, mock_data_service)

    @pytest.mark.asyncio
    async def test_add_answer_to_finished_flow_with_attachment(self, mock_entity_service, mock_cyoda_auth_service):
        """Test that add_answer_to_finished_flow correctly handles attachment_edge_message_id."""
        answer = "Test answer"
        attachment_id = "attachment_123"
        
        edge_id, last_modified = await add_answer_to_finished_flow(
            entity_service=mock_entity_service,
            answer=answer,
            cyoda_auth_service=mock_cyoda_auth_service,
            attachment_edge_message_id=attachment_id
        )
        
        # Verify the entity was created with attachment reference
        mock_entity_service.add_item.assert_called_once()
        call_args = mock_entity_service.add_item.call_args
        created_entity = call_args.kwargs['entity']
        
        assert created_entity.type == "answer"
        assert created_entity.message == answer
        assert created_entity.attachment_edge_message_id == attachment_id
        assert edge_id == "mock_edge_id_123"

    @pytest.mark.asyncio
    async def test_trigger_manual_transition_with_validation(self, mock_entity_service, mock_cyoda_auth_service, validation_service):
        """Test that trigger_manual_transition uses validation service for long answers."""
        # Create a long answer (250 words)
        long_answer = " ".join([f"word{i}" for i in range(250)])
        
        # Mock entity service to return different IDs for main and attachment
        mock_entity_service.add_item.side_effect = ["attachment_id_456", "main_edge_id_789"]
        
        # Create a mock chat entity
        chat = ChatEntity(
            user_id="test_user",
            chat_flow=ChatFlow(finished_flow=[]),
            workflow_name="test_workflow",
            memory_id="test_memory_id",
            technical_id="test_chat_id",
            current_state="active"
        )
        
        edge_id, transitioned = await trigger_manual_transition(
            entity_service=mock_entity_service,
            chat=chat,
            answer=long_answer,
            cyoda_auth_service=mock_cyoda_auth_service,
            validation_service=validation_service
        )
        
        # Verify that two entities were created (attachment + main)
        assert mock_entity_service.add_item.call_count == 2
        
        # Verify the attachment was created first
        first_call = mock_entity_service.add_item.call_args_list[0]
        attachment_entity = first_call.kwargs['entity']
        assert attachment_entity.type == "answer_attachment"
        assert attachment_entity.message == long_answer
        assert attachment_entity.publish is False
        
        # Verify the main answer was created with abridged content and attachment reference
        second_call = mock_entity_service.add_item.call_args_list[1]
        main_entity = second_call.kwargs['entity']
        assert main_entity.type == "answer"
        assert "[additional requirement]" in main_entity.message
        assert main_entity.attachment_edge_message_id == "attachment_id_456"
        
        # Verify the chat flow was updated with attachment reference
        assert len(chat.chat_flow.finished_flow) == 1
        flow_message = chat.chat_flow.finished_flow[0]
        assert flow_message.attachment_edge_message_id == "attachment_id_456"

    @pytest.mark.asyncio
    async def test_chat_service_add_chat_with_long_name(self, chat_service, mock_entity_service):
        """Test that ChatService.add_chat uses validation for long initial questions."""
        # Create a long initial question (250 words)
        long_question = " ".join([f"word{i}" for i in range(250)])
        
        # Mock entity service responses
        mock_entity_service.add_item.side_effect = [
            "greeting_id",      # greeting message
            "memory_id",        # memory
            "attachment_id",    # attachment for long answer
            "main_answer_id",   # main abridged answer
            "chat_id",          # chat entity
            "business_id"       # business entity
        ]
        
        result = await chat_service.add_chat(
            user_id="test_user",
            req_data={"name": long_question, "description": "Test description"}
        )
        
        # Verify that multiple entities were created including attachment
        assert mock_entity_service.add_item.call_count == 6
        
        # Check that the attachment was created for the long question
        attachment_call = mock_entity_service.add_item.call_args_list[2]
        attachment_entity = attachment_call.kwargs['entity']
        assert attachment_entity.type == "answer_attachment"
        assert attachment_entity.message == long_question
        
        # Check that the main answer was abridged
        main_answer_call = mock_entity_service.add_item.call_args_list[3]
        main_answer_entity = main_answer_call.kwargs['entity']
        assert main_answer_entity.type == "answer"
        assert "[additional requirement]" in main_answer_entity.message
        assert main_answer_entity.attachment_edge_message_id == "attachment_id"
        
        assert result["message"] == "Chat created"
        assert "technical_id" in result
        assert "answer_technical_id" in result

    @pytest.mark.asyncio
    async def test_short_answer_no_attachment_created(self, validation_service, mock_entity_service, mock_cyoda_auth_service):
        """Test that short answers don't create attachments."""
        short_answer = "This is a short answer."
        
        chat = ChatEntity(
            user_id="test_user",
            chat_flow=ChatFlow(finished_flow=[]),
            workflow_name="test_workflow",
            memory_id="test_memory_id",
            technical_id="test_chat_id",
            current_state="active"
        )
        
        mock_entity_service.add_item.return_value = "main_edge_id_only"
        
        edge_id, transitioned = await trigger_manual_transition(
            entity_service=mock_entity_service,
            chat=chat,
            answer=short_answer,
            cyoda_auth_service=mock_cyoda_auth_service,
            validation_service=validation_service
        )
        
        # Verify only one entity was created (no attachment)
        assert mock_entity_service.add_item.call_count == 1
        
        # Verify the main answer has no attachment reference
        call_args = mock_entity_service.add_item.call_args
        main_entity = call_args.kwargs['entity']
        assert main_entity.type == "answer"
        assert main_entity.message == short_answer
        assert main_entity.attachment_edge_message_id is None
        
        # Verify the chat flow has no attachment reference
        flow_message = chat.chat_flow.finished_flow[0]
        assert flow_message.attachment_edge_message_id is None

    @pytest.mark.asyncio
    async def test_submit_text_answer_with_long_text(self, chat_service, mock_entity_service):
        """Test that submit_text_answer uses validation for long text answers."""
        # Create a long text answer (250 words)
        long_answer = " ".join([f"word{i}" for i in range(250)])

        # Mock the chat retrieval
        mock_chat = ChatEntity(
            user_id="test_user",
            chat_flow=ChatFlow(finished_flow=[]),
            workflow_name="test_workflow",
            memory_id="test_memory_id",
            technical_id="test_chat_id",
            current_state="active"
        )

        # Mock the business entity and chat retrieval
        mock_business_entity = MagicMock()
        mock_business_entity.chat_id = "test_chat_id"
        mock_business_entity.user_id = "test_user"

        chat_service.entity_service.get_item.side_effect = [mock_business_entity, mock_chat]
        chat_service._get_user_id = MagicMock(return_value="test_user")

        # Mock entity service to return different IDs for attachment and main answer
        mock_entity_service.add_item.side_effect = ["attachment_id_789", "main_answer_id_456"]

        # Call submit_text_answer
        result = await chat_service.submit_text_answer(
            auth_header="Bearer test_token",
            technical_id="business_entity_id",
            answer=long_answer
        )

        # Verify that validation was applied (attachment created)
        assert mock_entity_service.add_item.call_count == 2

        # Verify attachment was created first
        first_call = mock_entity_service.add_item.call_args_list[0]
        attachment_entity = first_call.kwargs['entity']
        assert attachment_entity.type == "answer_attachment"
        assert attachment_entity.message == long_answer

        # Verify main answer was abridged
        second_call = mock_entity_service.add_item.call_args_list[1]
        main_entity = second_call.kwargs['entity']
        assert main_entity.type == "answer"
        assert "[additional requirement]" in main_entity.message
        assert main_entity.attachment_edge_message_id == "attachment_id_789"

    @pytest.mark.asyncio
    async def test_submit_answer_with_file_creates_blob(self, chat_service, mock_entity_service):
        """Test that submit_answer with file creates a file blob."""
        # Create a mock file
        mock_file = MagicMock()
        mock_file.filename = "test_document.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.content_length = 1024
        mock_file.read.return_value = b"PDF file content here"
        mock_file.seek = MagicMock()

        # Mock the chat retrieval
        mock_chat = ChatEntity(
            user_id="test_user",
            chat_flow=ChatFlow(finished_flow=[]),
            workflow_name="test_workflow",
            memory_id="test_memory_id",
            technical_id="test_chat_id",
            current_state="active"
        )

        # Mock the business entity and chat retrieval
        mock_business_entity = MagicMock()
        mock_business_entity.chat_id = "test_chat_id"
        mock_business_entity.user_id = "test_user"

        chat_service.entity_service.get_item.side_effect = [mock_business_entity, mock_chat]
        chat_service._get_user_id = MagicMock(return_value="test_user")

        # Mock get_user_message to avoid file reading issues - patch both locations
        with patch('services.chat_service.get_user_message', new_callable=AsyncMock) as mock_get_user_message1, \
             patch('common.utils.chat_util_functions.get_user_message', new_callable=AsyncMock) as mock_get_user_message2:
            mock_get_user_message1.return_value = "Here is my document: [file content]"
            mock_get_user_message2.return_value = "Here is my document: [file content]"

            # Mock entity service to return blob ID and main answer ID
            mock_entity_service.add_item.side_effect = ["blob_id_999", "main_answer_id_888"]

            # Call submit_answer with file
            result = await chat_service.submit_answer(
                auth_header="Bearer test_token",
                technical_id="business_entity_id",
                answer="Here is my document",
                user_file=mock_file
            )

            # Verify that file blob was created
            assert mock_entity_service.add_item.call_count == 2

            # Verify file blob was created first
            first_call = mock_entity_service.add_item.call_args_list[0]
            blob_entity = first_call.kwargs['entity']
            assert blob_entity.type == "file_blob"
            assert blob_entity.metadata["filename"] == "test_document.pdf"
            assert blob_entity.metadata["content_type"] == "application/pdf"
            assert blob_entity.metadata["user_id"] == "test_user"
            assert blob_entity.metadata["file_size"] == 21  # len(b"PDF file content here")

            # Verify main answer references the blob
            second_call = mock_entity_service.add_item.call_args_list[1]
            main_entity = second_call.kwargs['entity']
            assert main_entity.type == "answer"
            assert main_entity.file_blob_id == "blob_id_999"
            assert main_entity.attachment_edge_message_id is None  # No text attachment for file answers

    @pytest.mark.asyncio
    async def test_submit_answer_with_multiple_files_creates_blobs(self, chat_service, mock_entity_service):
        """Test that submit_answer with multiple files creates multiple blobs."""
        # Create mock files
        mock_file1 = MagicMock()
        mock_file1.filename = "report1.txt"
        mock_file1.content_type = "text/plain"
        mock_file1.content_length = 500
        mock_file1.read.return_value = b"Content of first file"
        mock_file1.seek = MagicMock()

        mock_file2 = MagicMock()
        mock_file2.filename = "report2.pdf"
        mock_file2.content_type = "application/pdf"
        mock_file2.content_length = 1000
        mock_file2.read.return_value = b"Content of second file"
        mock_file2.seek = MagicMock()

        # Mock the chat retrieval
        mock_chat = ChatEntity(
            user_id="test_user",
            chat_flow=ChatFlow(finished_flow=[]),
            workflow_name="test_workflow",
            memory_id="test_memory_id",
            technical_id="test_chat_id",
            current_state="active"
        )

        # Mock the business entity and chat retrieval
        mock_business_entity = MagicMock()
        mock_business_entity.chat_id = "test_chat_id"
        mock_business_entity.user_id = "test_user"

        chat_service.entity_service.get_item.side_effect = [mock_business_entity, mock_chat]
        chat_service._get_user_id = MagicMock(return_value="test_user")

        # Mock get_user_message to avoid file reading issues
        with patch('services.chat_service.get_user_message', new_callable=AsyncMock) as mock_get_user_message1, \
             patch('common.utils.chat_util_functions.get_user_message', new_callable=AsyncMock) as mock_get_user_message2:

            mock_get_user_message1.return_value = "This is my answer with multiple files attached."
            mock_get_user_message2.return_value = "This is my answer with multiple files attached."

            # Mock entity service to return blob IDs and main answer ID
            mock_entity_service.add_item.side_effect = ["blob_id_1", "blob_id_2", "main_answer_id_999"]

            # Call submit_answer with multiple files
            result = await chat_service.submit_answer(
                auth_header="Bearer test_token",
                technical_id="business_entity_id",
                answer="This is my answer with multiple files attached.",
                user_files=[mock_file1, mock_file2]
            )

            # Verify that both file blobs were created and main answer references them
            assert mock_entity_service.add_item.call_count == 3

            # Verify first file blob was created
            first_call = mock_entity_service.add_item.call_args_list[0]
            first_blob = first_call.kwargs['entity']
            assert first_blob.type == "file_blob"
            assert first_blob.metadata["filename"] == "report1.txt"

            # Verify second file blob was created
            second_call = mock_entity_service.add_item.call_args_list[1]
            second_blob = second_call.kwargs['entity']
            assert second_blob.type == "file_blob"
            assert second_blob.metadata["filename"] == "report2.pdf"

            # Verify main answer references both blobs
            third_call = mock_entity_service.add_item.call_args_list[2]
            main_entity = third_call.kwargs['entity']
            assert main_entity.type == "answer"
            assert main_entity.message == "This is my answer with multiple files attached."
            assert main_entity.file_blob_ids == ["blob_id_1", "blob_id_2"]
            # For multiple files, file_blob_id should be set to first file for backward compatibility
            assert main_entity.file_blob_id == "blob_id_1"
            assert main_entity.attachment_edge_message_id is None


