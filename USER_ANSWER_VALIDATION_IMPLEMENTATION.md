# User Answer Validation Service Implementation

## Overview

This implementation adds a user answer validation service that automatically processes user answers based on word count. When a user answer exceeds 200 words (without a file attachment), the system creates an abridged version for the main flow and stores the full answer as an attachment.

## Key Features

- **Word Count Validation**: Automatically counts words in user answers
- **Abridged Version Creation**: For answers > 200 words, creates a summary with first 100 words + "[additional requirement]" + last 100 words
- **Attachment Storage**: Full answer is saved as a separate edge message with type "answer_attachment"
- **File Blob Storage**: Files are saved as base64-encoded edge messages with type "file_blob" and metadata
- **File-Only Submissions**: When only a file is provided (no/minimal answer text), file content becomes the answer
- **File Content Abridging**: Long file content (>200 words) is abridged to first 100 + last 100 words when used as answer
- **File Handling**: Files are always stored as blobs, with content optionally used as explanatory text
- **Seamless Integration**: Works with existing chat flow without breaking changes

## Implementation Details

### 1. Model Changes

**File**: `entity/model.py`
- Added `attachment_edge_message_id: Optional[str] = None` field to `FlowEdgeMessage` model
- Added `file_blob_id: Optional[str] = None` field to `FlowEdgeMessage` model
- Added `metadata: Optional[Dict[str, Any]] = None` field to `FlowEdgeMessage` model
- These fields link the main answer to its full-text attachment and/or file blob when needed

### 2. User Answer Validation Service

**File**: `services/user_answer_validation_service.py`
- **Class**: `UserAnswerValidationService`
- **Main Method**: `validate_and_process_answer(answer, user_file=None, user_id=None)`
- **Logic**:
  - If file provided: saves file as base64-encoded blob with metadata
  - If file provided + no/minimal answer: reads file content and uses as answer (abridged if >200 words)
  - If file provided + substantial answer: uses provided answer text
  - If no file + ≤ 200 words: returns answer unchanged
  - If no file + > 200 words: creates abridged version and saves full version as attachment
  - Returns tuple: `(processed_answer, attachment_edge_message_id, file_blob_id)`
- **File Blob Storage**: `_save_file_as_blob()` method handles file encoding and metadata storage
- **File Content Reading**: `_read_file_content_for_answer()` method reads file content for use as answer text

### 3. Utility Function Updates

**File**: `common/utils/chat_util_functions.py`
- **Updated**: `add_answer_to_finished_flow()` - now accepts `attachment_edge_message_id` and `file_blob_id` parameters
- **Updated**: `trigger_manual_transition()` - now accepts `validation_service` parameter and uses it to process answers and files
- **Enhanced**: FlowEdgeMessage creation to include attachment and file blob references

### 4. Chat Service Integration

**File**: `services/chat_service.py`
- **Updated**: Constructor to initialize `UserAnswerValidationService`
- **Updated**: `add_chat()` method to use validation for initial questions
- **Updated**: `submit_text_answer()` method to explicitly pass `user_file=None` for consistent validation
- **Updated**: `submit_answer()` method to pass file information for proper validation logic
- **Updated**: `approve()` method to explicitly pass `user_file=None` for consistency
- **Updated**: `_submit_answer_helper()` to pass validation service to transition functions
- **Seamless**: All existing functionality preserved while adding validation

## Usage Examples

### Short Answer (≤ 200 words)
```python
# Input: "This is a short answer."
# Output: 
# - processed_answer: "This is a short answer."
# - attachment_edge_message_id: None
```

### Long Answer (> 200 words)
```python
# Input: 250-word answer
# Output:
# - processed_answer: "first 100 words... [additional requirement] ...last 100 words"
# - attachment_edge_message_id: "attachment_123"
# - Full answer saved separately with ID "attachment_123"
```

### Answer with File (Substantial Text)
```python
# Input: Substantial answer + file attachment (e.g., "Here's my analysis: ..." + document.pdf)
# Output:
# - processed_answer: Original answer (unchanged)
# - attachment_edge_message_id: None
# - file_blob_id: "blob_456" (file saved as base64-encoded edge message)
# - File metadata stored: filename, content_type, file_size, encoding, user_id
```

### File-Only Submission (No/Minimal Text)
```python
# Input: Empty/minimal answer + file attachment (e.g., "" + report.txt with content)
# File content: "This is a detailed report with analysis and conclusions..."
# Output:
# - processed_answer: File content used as answer (abridged if >200 words)
# - attachment_edge_message_id: None (no text attachment needed)
# - file_blob_id: "blob_789" (file saved as base64-encoded edge message)
# - File metadata stored: filename, content_type, file_size, encoding, user_id
```

## Data Flow

1. **User submits answer** → ChatService receives it
2. **Validation service processes** → Checks word count and file presence
3. **If > 200 words without file**:
   - Creates abridged version (first 100 + "[additional requirement]" + last 100)
   - Saves full answer as attachment edge message
   - Returns both processed answer and attachment ID
4. **Main answer created** → With references to attachment and/or file blob if applicable
5. **Chat flow updated** → FlowEdgeMessage includes attachment and file blob references
6. **Response sent** → User sees confirmation with answer ID

## Testing

### Unit Tests
**File**: `tests/services/test_user_answer_validation_service.py`
- Tests all word count scenarios (short, exact 200, 201+)
- Tests file attachment handling and blob storage
- Tests attachment creation and referencing
- **NEW**: Tests file-only submissions using file content as answer
- **NEW**: Tests long file content abridging when used as answer
- **NEW**: Tests substantial answer precedence over file content

### Integration Tests
**File**: `tests/integration/test_user_answer_validation_integration.py`
- Tests end-to-end flow through ChatService
- Tests trigger_manual_transition integration
- Tests attachment linking in chat flow
- Tests both short and long answer scenarios
- **NEW**: Tests `submit_text_answer()` method with long text validation
- **NEW**: Tests `submit_answer()` with file creates blob storage

### Test Results
- ✅ All unit tests pass (9/9)
- ✅ All integration tests pass (6/6)
- ✅ Existing chat service tests updated and passing
- ✅ File blob storage functionality fully tested
- ✅ File-only submission functionality fully tested

### API Coverage
All answer submission methods now use validation:
- ✅ `add_chat()` - validates initial questions
- ✅ `submit_text_answer()` - validates text-only answers
- ✅ `submit_answer()` - validates answers with optional files, uses file content as answer when no text provided
- ✅ `approve()` - validates approval responses (typically short)

## Configuration

The validation uses a hard-coded 200-word limit. This can be made configurable by:
1. Adding `MAX_ANSWER_WORDS = 200` to `common/config/config.py`
2. Updating the validation service to use `config.MAX_ANSWER_WORDS`

## Backward Compatibility

- ✅ All existing APIs unchanged
- ✅ Existing FlowEdgeMessage objects work (attachment_edge_message_id is optional)
- ✅ No breaking changes to chat flow
- ✅ File handling preserved
- ✅ All existing tests pass with minimal updates

## Future Enhancements

1. **Configurable Word Limits**: Make the 200-word threshold configurable
2. **Smart Summarization**: Use AI to create better summaries instead of simple truncation
3. **Attachment Retrieval API**: Add endpoints to retrieve full text from attachments
4. **UI Integration**: Display attachment indicators in the chat interface
5. **Compression**: Compress large text attachments for storage efficiency
