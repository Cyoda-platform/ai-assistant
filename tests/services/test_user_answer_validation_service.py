import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.user_answer_validation_service import UserAnswerValidationService


class TestUserAnswerValidationService:
    
    @pytest.fixture
    def mock_entity_service(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_cyoda_auth_service(self):
        return MagicMock()
    
    @pytest.fixture
    def validation_service(self, mock_entity_service, mock_cyoda_auth_service):
        return UserAnswerValidationService(mock_entity_service, mock_cyoda_auth_service)

    @pytest.mark.asyncio
    async def test_validate_short_answer_no_processing(self, validation_service):
        """Test that answers with 200 words or less are returned unchanged."""
        short_answer = "This is a short answer with less than 200 words."
        
        result_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=short_answer,
            user_files=None
        )

        assert result_answer == short_answer
        assert file_blob_ids is None

    @pytest.mark.asyncio
    async def test_validate_empty_answer(self, validation_service):
        """Test that empty answers are handled correctly."""
        result_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer="",
            user_files=None
        )

        assert result_answer == ""        assert file_blob_ids == []  # Empty list, not None (files_to_process is initialized as [])

    @pytest.mark.asyncio
    async def test_validate_answer_with_file_no_processing(self, validation_service, mock_entity_service):
        """Test that long answers with files are abridged and original saved as blob."""
        long_answer = " ".join(["word"] * 300)  # 300 words > 200
        mock_file = MagicMock()
        mock_file.filename = "test_file.txt"
        mock_file.content_type = "text/plain"
        mock_file.read.return_value = b"file content"
        mock_file.seek = MagicMock()

        # Mock entity service to return blob IDs (file blob, then original message blob)
        mock_entity_service.add_item.side_effect = ["blob_file", "blob_original"]

        result_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=long_answer,
            user_files=[mock_file],
            user_id="test_user"
        )

        # With new logic: message > N words and files -> message = abridged(message), files = files + file for initial message
        expected_first_100 = " ".join(["word"] * 100)
        expected_last_100 = " ".join(["word"] * 100)
        expected_abridged = f"{expected_first_100} [additional requirement] {expected_last_100}"

        assert result_answer == expected_abridged  # Answer abridged        assert file_blob_ids == ["blob_file", "blob_original"]  # File + original message as blobs

        # Verify entity service was called twice (file blob + original message blob)
        assert mock_entity_service.add_item.call_count == 2
        mock_file.read.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_long_answer_creates_abridged_version(self, validation_service, mock_entity_service):
        """Test that long answers are abridged and full version is saved as attachment."""
        # Create a 250-word answer
        words = [f"word{i}" for i in range(250)]
        long_answer = " ".join(words)
        
        # Mock the entity service to return an attachment ID
        mock_entity_service.add_item.return_value = "attachment_123"
        
        result_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=long_answer,
            user_files=None
        )

        # Check that the result is abridged
        expected_first_100 = " ".join(words[:100])
        expected_last_100 = " ".join(words[-100:])
        expected_abridged = f"{expected_first_100} [additional requirement] {expected_last_100}"

        assert result_answer == expected_abridged
        assert file_blob_ids == ["attachment_123"]        mock_entity_service.add_item.assert_called_once()
        call_args = mock_entity_service.add_item.call_args
        saved_entity = call_args.kwargs['entity']
        
        assert saved_entity.type == "answer_attachment"
        assert saved_entity.message == long_answer
        assert saved_entity.publish is False
        assert saved_entity.consumed is True

    @pytest.mark.asyncio
    async def test_validate_exactly_200_words_no_processing(self, validation_service):
        """Test that answers with exactly 200 words are not processed."""
        words = [f"word{i}" for i in range(200)]
        answer_200_words = " ".join(words)
        
        result_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=answer_200_words,
            user_files=None
        )

        assert result_answer == answer_200_words        assert file_blob_ids is None

    @pytest.mark.asyncio
    async def test_validate_201_words_gets_processed(self, validation_service, mock_entity_service):
        """Test that answers with 201 words get processed."""
        words = [f"word{i}" for i in range(201)]
        answer_201_words = " ".join(words)
        
        mock_entity_service.add_item.return_value = "attachment_456"
        
        result_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=answer_201_words,
            user_files=None
        )

        # Should be abridged
        expected_first_100 = " ".join(words[:100])
        expected_last_100 = " ".join(words[-100:])
        expected_abridged = f"{expected_first_100} [additional requirement] {expected_last_100}"

        assert result_answer == expected_abridged        assert file_blob_ids is None

    @pytest.mark.asyncio
    async def test_file_only_submission_uses_file_content_as_answer(self, validation_service, mock_entity_service):
        """Test that when only file is provided (no answer), file content becomes the answer."""
        # Create a mock file with content
        mock_file = MagicMock()
        mock_file.filename = "document.txt"
        mock_file.content_type = "text/plain"
        mock_file.content_length = 500
        mock_file.read.return_value = b"This is file content that should be used as the answer text."
        mock_file.seek = MagicMock()

        # Mock file reading
        with patch('common.utils.file_reader.read_file_content') as mock_read_file:
            mock_read_file.return_value = "This is file content that should be used as the answer text."

            # Mock entity service for blob storage
            mock_entity_service.add_item.return_value = "blob_id_123"

            # Test with empty answer
            processed_answer, file_blob_ids = await validation_service.validate_and_process_answer(
                answer="",
                user_files=[mock_file],
                user_id="test_user"
            )

            # Verify file content was used as answer
            assert processed_answer == "This is file content that should be used as the answer text."            assert file_blob_ids == ["blob_id_123"]  # File was saved as blob

            # Verify blob was created
            mock_entity_service.add_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_file_only_submission_with_long_content_gets_abridged(self, validation_service, mock_entity_service):
        """Test that long file content gets abridged when used as answer."""
        # Create long file content (250 words)
        long_content = " ".join([f"word{i}" for i in range(250)])

        mock_file = MagicMock()
        mock_file.filename = "long_document.txt"
        mock_file.content_type = "text/plain"
        mock_file.content_length = 2000
        mock_file.read.return_value = long_content.encode()
        mock_file.seek = MagicMock()

        # Mock file reading
        with patch('common.utils.file_reader.read_file_content') as mock_read_file:
            mock_read_file.return_value = long_content

            # Mock entity service for blob storage
            mock_entity_service.add_item.return_value = "blob_id_456"

            # Test with minimal answer
            processed_answer, file_blob_ids = await validation_service.validate_and_process_answer(
                answer="",
                user_files=[mock_file],
                user_id="test_user"
            )

            # Verify file content was abridged
            assert "[additional content]" in processed_answer
            assert processed_answer.startswith("word0 word1")  # First 100 words
            assert processed_answer.endswith("word248 word249")  # Last 100 words            assert file_blob_ids == ["blob_id_456"]  # File was saved as blob

    @pytest.mark.asyncio
    async def test_file_with_substantial_answer_uses_answer_text(self, validation_service, mock_entity_service):
        """Test that when substantial answer is provided with file, answer text is used."""
        mock_file = MagicMock()
        mock_file.filename = "document.txt"
        mock_file.content_type = "text/plain"
        mock_file.content_length = 500
        mock_file.read.return_value = b"File content here"
        mock_file.seek = MagicMock()

        # Mock entity service for blob storage
        mock_entity_service.add_item.return_value = "blob_id_789"

        substantial_answer = "This is a substantial answer that explains the file content in detail."

        # Test with substantial answer
        processed_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=substantial_answer,
            user_files=[mock_file],
            user_id="test_user"
        )

        # Verify original answer was used (not file content)
        assert processed_answer == substantial_answer        assert file_blob_ids == ["blob_id_789"]  # File was saved as blob

    @pytest.mark.asyncio
    async def test_multiple_files_submission(self, validation_service, mock_entity_service):
        """Test that multiple files are all saved as blobs."""
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

        # Mock entity service to return blob IDs
        mock_entity_service.add_item.side_effect = ["blob_id_1", "blob_id_2"]

        # Call with multiple files and substantial answer
        result = await validation_service.validate_and_process_answer(
            answer="This is my answer with multiple files attached.",
            user_files=[mock_file1, mock_file2],
            user_id="test_user"
        )

        processed_answer, attachment_id, file_blob_ids = result

        # Verify that answer text is used and both files are saved
        assert processed_answer == "This is my answer with multiple files attached."        assert file_blob_ids == ["blob_id_1", "blob_id_2"]  # Both files saved as blobs

        # Verify both file blobs were created
        assert mock_entity_service.add_item.call_count == 2

        # Check first file blob
        first_call = mock_entity_service.add_item.call_args_list[0]
        first_blob = first_call.kwargs['entity']
        assert first_blob.type == "file_blob"
        assert first_blob.metadata["filename"] == "report1.txt"

        # Check second file blob
        second_call = mock_entity_service.add_item.call_args_list[1]
        second_blob = second_call.kwargs['entity']
        assert second_blob.type == "file_blob"
        assert second_blob.metadata["filename"] == "report2.pdf"

    @pytest.mark.asyncio
    async def test_multiple_files_with_minimal_answer_uses_first_file_content(self, validation_service, mock_entity_service):
        """Test that with multiple files and minimal answer, first file content is used as answer."""
        # Create mock files
        mock_file1 = MagicMock()
        mock_file1.filename = "report1.txt"
        mock_file1.content_type = "text/plain"
        mock_file1.content_length = 500
        mock_file1.read.return_value = b"This is the content of the first file that should become the answer."
        mock_file1.seek = MagicMock()

        mock_file2 = MagicMock()
        mock_file2.filename = "report2.pdf"
        mock_file2.content_type = "application/pdf"
        mock_file2.content_length = 1000
        mock_file2.read.return_value = b"Content of second file"
        mock_file2.seek = MagicMock()

        # Mock entity service to return blob IDs
        mock_entity_service.add_item.side_effect = ["blob_id_1", "blob_id_2"]

        # Mock file reading for first file only
        with patch('common.utils.file_reader.read_file_content') as mock_read_file:
            mock_read_file.return_value = "This is the content of the first file that should become the answer."

            # Call with multiple files and minimal answer
            result = await validation_service.validate_and_process_answer(
                answer="",  # Empty answer - should use first file content
                user_files=[mock_file1, mock_file2],
                user_id="test_user"
            )

            processed_answer, attachment_id, file_blob_ids = result

            # Verify that first file content is used as answer
            assert processed_answer == "This is the content of the first file that should become the answer."            assert file_blob_ids == ["blob_id_1", "blob_id_2"]  # Both files saved as blobs

            # Verify file reading was called only for first file
            mock_read_file.assert_called_once_with(mock_file1)

            # Verify both file blobs were created
            assert mock_entity_service.add_item.call_count == 2

    @pytest.mark.asyncio
    async def test_comprehensive_message_handling_scenarios(self, validation_service, mock_entity_service):
        """Test all comprehensive message handling scenarios."""

        # Scenario 1: message < N words and no file -> message = message
        short_answer = "This is a short answer with only ten words here."
        processed_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=short_answer,
            user_files=None,
            user_id="test_user"
        )
        assert processed_answer == short_answer        assert file_blob_ids is None

        # Scenario 2: message > N words and no file -> message = abridged(message), save as txt edge message
        long_words = [f"word{i}" for i in range(250)]  # 250 words > 200
        long_answer = " ".join(long_words)

        mock_entity_service.add_item.return_value = "attachment_id_123"

        processed_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=long_answer,
            user_files=None,
            user_id="test_user"
        )

        expected_first_100 = " ".join(long_words[:100])
        expected_last_100 = " ".join(long_words[-100:])
        expected_abridged = f"{expected_first_100} [additional requirement] {expected_last_100}"

        assert processed_answer == expected_abridged
        assert file_blob_ids == ["attachment_id_123"]  # Full message saved as attachment
        assert file_blob_ids is None

        # Scenario 3: message < N words and files -> message = message, files = files
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.content_length = 100
        mock_file.read.return_value = b"file content"
        mock_file.seek = MagicMock()

        mock_entity_service.add_item.return_value = "blob_id_123"

        processed_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=short_answer,
            user_files=[mock_file],
            user_id="test_user"
        )

        assert processed_answer == short_answer  # Original message kept        assert file_blob_ids == ["blob_id_123"]  # File saved as blob

    @pytest.mark.asyncio
    async def test_long_message_with_files_scenario(self, validation_service, mock_entity_service):
        """Test scenario 4: message > N words and files -> message = abridged(message), files = files + file for initial message"""
        # Create long message (250 words > 200)
        long_words = [f"word{i}" for i in range(250)]
        long_answer = " ".join(long_words)

        # Create mock file
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.content_length = 100
        mock_file.read.return_value = b"file content"
        mock_file.seek = MagicMock()

        # Set up mock to return different IDs for file blob and original message blob
        mock_entity_service.add_item.side_effect = ["blob_id_file", "blob_id_original"]

        processed_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=long_answer,
            user_files=[mock_file],
            user_id="test_user"
        )

        expected_first_100 = " ".join(long_words[:100])
        expected_last_100 = " ".join(long_words[-100:])
        expected_abridged = f"{expected_first_100} [additional requirement] {expected_last_100}"

        assert processed_answer == expected_abridged  # Message abridged        assert file_blob_ids == ["blob_id_file", "blob_id_original"]  # File + original message as blobs

    @pytest.mark.asyncio
    async def test_empty_message_with_files_scenario(self, validation_service, mock_entity_service):
        """Test scenario 5: empty message and files -> message = first file content (abridged if needed)"""
        file_content = "This is the content from the file that will be used as the message."

        # Create mock file
        mock_file = MagicMock()
        mock_file.filename = "content.txt"
        mock_file.content_type = "text/plain"
        mock_file.content_length = 100
        mock_file.read.return_value = file_content.encode()
        mock_file.seek = MagicMock()

        with patch('common.utils.file_reader.read_file_content') as mock_read_file:
            mock_read_file.return_value = file_content
            mock_entity_service.add_item.return_value = "blob_id_file_content"

            processed_answer, file_blob_ids = await validation_service.validate_and_process_answer(
                answer="",  # Empty answer
                user_files=[mock_file],
                user_id="test_user"
            )

            assert processed_answer == file_content  # File content used as message            assert file_blob_ids == ["blob_id_file_content"]  # File saved as blob

            # Verify file reading was called
            mock_read_file.assert_called_with(mock_file)

    @pytest.mark.asyncio
    async def test_single_file_conversion_at_endpoint_level(self, validation_service, mock_entity_service):
        """Test that single file conversion happens at endpoint level, validation service only uses user_files."""
        answer = "Short answer with single file"

        # Create mock file
        mock_file = MagicMock()
        mock_file.filename = "single_file.txt"
        mock_file.content_type = "text/plain"
        mock_file.content_length = 100
        mock_file.read.return_value = b"single file content"
        mock_file.seek = MagicMock()

        mock_entity_service.add_item.return_value = "blob_single_file"

        # Test with user_files parameter (conversion already happened at endpoint level)
        processed_answer, file_blob_ids = await validation_service.validate_and_process_answer(
            answer=answer,
            user_files=[mock_file],  # Single file converted to list at endpoint level
            user_id="test_user"
        )

        # Should work exactly the same as multiple files
        assert processed_answer == answer  # Short message kept as-is        assert file_blob_ids == ["blob_single_file"]  # File saved as blob

        # Verify entity service was called once for the file blob
        mock_entity_service.add_item.assert_called_once()
