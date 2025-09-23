import logging
import base64
from typing import Tuple, Optional, List

import common.config.const as const
from common.config.config import config
from common.utils.utils import get_current_timestamp_num
from entity.model import FlowEdgeMessage

logger = logging.getLogger(__name__)


class UserAnswerValidationService:
    def __init__(self, entity_service, cyoda_auth_service):
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service

    async def validate_and_process_answer(
        self,
        answer: str,
        user_files=None,
        user_id: str = None
    ) -> Tuple[str, Optional[List[str]]]:
        """
        Validates user answer and processes it according to comprehensive message handling rules.

        Logic:
        - if message < N words and no file -> message = message
        - if message > N words and no file -> message = abridged(message), save full message as txt edge message
        - if message < N words and files -> message = message, files = files
        - if message > N words and files -> message = abridged(message), files = files + file for initial message
        - if message empty/minimal and files -> message = first file content (abridged if needed)

        Args:
            answer: The user's answer text
            user_file: Optional single file attachment (deprecated, use user_files)
            user_files: Optional list of file attachments
            user_id: Optional user ID for blob storage tracking

        Returns:
            Tuple of (processed_answer, file_blob_ids)
            - processed_answer: The answer to use in the main flow
            - file_blob_ids: List of all edge message IDs (attachments and file blobs), None if none
        """
        # Handle multiple files (user_file conversion happens at endpoint level)
        files_to_process = user_files if user_files else []

        # Save all files as blobs
        file_blob_ids = []
        if files_to_process:
            logger.info(f"Processing {len(files_to_process)} file(s)")
            for file in files_to_process:
                logger.info(f"File provided, saving as blob: {getattr(file, 'filename', 'unknown')}")
                blob_id = await self._save_file_as_blob(file, user_id)
                file_blob_ids.append(blob_id)

        # Check if answer is empty/minimal - keep original message unchanged
        if not answer or len(answer.strip()) < 10:  # Less than 10 characters considered minimal
            if files_to_process:
                logger.info("Answer is minimal with files attached - keeping original message unchanged, file processing will be handled by AI agent handler")
                # Return original answer unchanged, let AI agent handler process file content
                return answer, file_blob_ids
            # If no files and minimal answer, return as-is
            return answer, file_blob_ids

        # Answer is substantial - apply the comprehensive logic
        words = answer.split()
        word_count = len(words)

        if word_count <= 350:  # N = 200 words
            # Message < N words
            if files_to_process:
                answer = f"{answer} [{const.USER_ATTACHED_FILE_MESSAGE}]"
                # message < N and files -> message = message, files = files
                logger.info(f"Short message ({word_count} words) with {len(files_to_process)} files - keeping both")
                return answer, file_blob_ids
            else:
                # message < N and no file -> message = message
                logger.info(f"Short message ({word_count} words) with no files - keeping as-is")
                return answer, None
        else:
            # Message > N words - treat exclusively as files, no message content
            if files_to_process:
                # message > N and files -> message = None, files = files + file for initial message
                logger.info(f"Long message ({word_count} words) with {len(files_to_process)} files - saving original as file, no message content")

                # Save the original full message as a text file blob
                original_message_blob_id = await self._save_text_as_blob(answer, "original_message.txt", user_id)
                file_blob_ids.append(original_message_blob_id)

                return None, file_blob_ids
            else:
                # message > N and no file -> message = None, save as txt edge message the full message
                logger.info(f"Long message ({word_count} words) with no files - saving full as file, no message content")
                attachment_id = await self._save_full_answer_as_attachment(answer)
                return None, [attachment_id]

        # This should not be reached due to the logic above, but keeping as fallback
        return answer, None

    async def _save_full_answer_as_attachment(self, full_answer: str) -> str:
        """
        Saves the full answer as a file blob.

        Args:
            full_answer: The complete user answer

        Returns:
            The edge message ID of the saved file blob
        """
        return await self._save_text_as_blob(full_answer, "user_message.txt", "system")

    async def _save_file_as_blob(self, user_file, user_id: str = None) -> str:
        """
        Saves a file as a blob edge message.

        Args:
            user_file: The uploaded file object
            user_id: Optional user ID for tracking

        Returns:
            The edge message ID of the saved blob
        """
        if not user_file:
            raise ValueError("No file provided")

        # Read file content as bytes
        user_file.seek(0)
        file_content = user_file.read()

        # Encode file content as base64 for storage
        encoded_content = base64.b64encode(file_content).decode('utf-8')

        # Get file metadata
        filename = getattr(user_file, 'filename', 'unknown_file')
        content_type = getattr(user_file, 'content_type', 'application/octet-stream')
        file_size = len(file_content)

        logger.info(f"Saving file blob: {filename} ({file_size} bytes, {content_type})")

        # Create blob metadata
        blob_metadata = {
            "filename": filename,
            "content_type": content_type,
            "file_size": file_size,
            "encoding": "base64"
        }

        # Add user_id if provided
        if user_id:
            blob_metadata["user_id"] = user_id

        # Create blob edge message
        last_modified = get_current_timestamp_num()
        blob_flow_message = FlowEdgeMessage(
            type="file_blob",
            message=encoded_content,  # Base64 encoded file content
            publish=False,  # Blobs are not published to the main flow
            consumed=True,
            last_modified=last_modified,
            metadata=blob_metadata
        )

        # Save blob to entity service
        blob_edge_message_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
            entity_version=config.ENTITY_VERSION,
            entity=blob_flow_message,
            meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
        )

        logger.info(f"File blob saved with ID: {blob_edge_message_id}")
        return blob_edge_message_id

    async def _read_file_content_for_answer(self, user_file) -> Optional[str]:
        """
        Reads file content for use as answer text.

        Args:
            user_file: The uploaded file object

        Returns:
            String content of the file, or None if reading fails
        """
        try:
            from common.utils.file_reader import read_file_content
            return read_file_content(user_file)
        except Exception as e:
            logger.error(f"Failed to read file content for answer: {e}")
            return None

    async def _save_text_as_blob(self, text_content: str, filename: str, user_id: str = None) -> str:
        """
        Saves text content as a file blob.

        Args:
            text_content: The text content to save
            filename: The filename to use for the blob
            user_id: Optional user ID for tracking

        Returns:
            The blob edge message ID
        """
        import base64
        from common.utils.utils import get_current_timestamp_num

        # Encode text as UTF-8 bytes, then base64
        text_bytes = text_content.encode('utf-8')
        base64_content = base64.b64encode(text_bytes).decode('utf-8')

        # Create blob metadata
        blob_metadata = {
            "filename": filename,
            "content_type": "text/plain",
            "file_size": len(text_bytes),
            "encoding": "base64",
            "user_id": user_id or "default"
        }

        # Create blob entity
        blob_entity = FlowEdgeMessage(
            type="file_blob",
            message=base64_content,
            publish=False,
            consumed=True,
            last_modified=get_current_timestamp_num(),
            metadata=blob_metadata
        )

        # Save the blob
        blob_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
            entity_version=config.ENTITY_VERSION,
            entity=blob_entity,
            meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
        )

        logger.info(f"Saved text as blob: {filename} (size: {len(text_bytes)} bytes)")
        return blob_id
