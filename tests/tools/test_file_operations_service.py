import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from tools.file_operations_service import FileOperationsService
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
import common.config.const as const


class TestFileOperationsService:
    """Test cases for FileOperationsService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for FileOperationsService."""
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
        """Create FileOperationsService instance."""
        return FileOperationsService(**mock_dependencies)

    @pytest.fixture
    def mock_chat_entity(self):
        """Create mock ChatEntity."""
        entity = MagicMock(spec=ChatEntity)
        entity.workflow_cache = {const.GIT_BRANCH_PARAM: "test_branch"}
        entity.workflow_name = "test_workflow"
        entity.failed = False
        entity.error = None
        return entity

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {const.GIT_BRANCH_PARAM: "test_branch"}
        entity.workflow_name = "test_workflow"
        entity.failed = False
        entity.error = None
        return entity

    @pytest.mark.asyncio
    async def test_save_env_file_success(self, service, mock_chat_entity):
        """Test successful environment file saving."""
        with patch('common.utils.utils.get_repository_name', return_value="test_repo"), \
             patch('common.utils.utils.get_project_file_name', return_value="/path/to/file.env"), \
             patch('aiofiles.open', mock_open(read_data="CHAT_ID_VAR=placeholder")) as mock_file, \
             patch('common.utils.utils._git_push', new_callable=AsyncMock) as mock_git_push:
            
            result = await service.save_env_file("tech_id", mock_chat_entity, filename="test.env")
            
            assert result == "Environment file saved successfully"
            mock_git_push.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_env_file_error(self, service, mock_chat_entity):
        """Test environment file saving with error."""
        with patch('common.utils.utils.get_repository_name', side_effect=Exception("Test error")):
            result = await service.save_env_file("tech_id", mock_chat_entity, filename="test.env")
            
            assert "Error saving environment file" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_save_file_python_success(self, service, mock_chat_entity):
        """Test successful file saving for Python repository."""
        # Mock all the external dependencies
        with patch('common.utils.utils.get_repository_name', return_value="python_repo"), \
             patch('common.utils.utils._save_file', new_callable=AsyncMock) as mock_save, \
             patch('common.utils.utils._git_push', new_callable=AsyncMock), \
             patch('common.utils.utils.get_project_file_name', return_value="/test/path/test.py"):

            result = await service.save_file(
                "tech_id", mock_chat_entity,
                filename="test.py", new_content="print('hello')"
            )

            assert result == "File saved successfully"
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_file_java_success(self, service, mock_chat_entity):
        """Test successful file saving for Java repository."""
        with patch('common.utils.utils.get_repository_name', return_value="java_repo"), \
             patch('common.utils.utils._save_file', new_callable=AsyncMock) as mock_save:
            
            result = await service.save_file(
                "tech_id", mock_chat_entity,
                filename="Test.java", new_content="public class Test {}"
            )
            
            assert result == "File saved successfully"
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_file_missing_params(self, service, mock_chat_entity):
        """Test file saving with missing parameters."""
        result = await service.save_file("tech_id", mock_chat_entity, filename="test.py")
        
        assert "Missing required parameters" in result

    @pytest.mark.asyncio
    async def test_read_file_success(self, service, mock_chat_entity):
        """Test successful file reading."""
        with patch('common.utils.utils.read_file_util', new_callable=AsyncMock, return_value="file content"), \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):
            
            result = await service.read_file("tech_id", mock_chat_entity, filename="test.py")
            
            assert result == "file content"

    @pytest.mark.asyncio
    async def test_read_file_missing_filename(self, service, mock_chat_entity):
        """Test file reading with missing filename."""
        result = await service.read_file("tech_id", mock_chat_entity)
        
        assert "Missing required parameters" in result

    @pytest.mark.asyncio
    async def test_clone_repo_success(self, service, mock_chat_entity):
        """Test successful repository cloning."""
        with patch('common.utils.utils.get_repository_name', return_value="test_repo"), \
             patch('common.utils.utils.clone_repo', new_callable=AsyncMock) as mock_clone, \
             patch('common.utils.utils._save_file', new_callable=AsyncMock) as mock_save, \
             patch('common.config.const.BRANCH_READY_NOTIFICATION', "Branch {git_branch} ready for {repository_name}"):
            
            result = await service.clone_repo("tech_id", mock_chat_entity)
            
            assert "Branch tech_id ready for test_repo" in result
            mock_clone.assert_called_once()
            mock_save.assert_called_once()
            assert mock_chat_entity.workflow_cache[const.GIT_BRANCH_PARAM] == "tech_id"

    @pytest.mark.asyncio
    async def test_delete_files_success(self, service, mock_agentic_entity):
        """Test successful file deletion."""
        with patch('common.utils.utils.delete_file', new_callable=AsyncMock) as mock_delete, \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):
            
            result = await service.delete_files(
                "tech_id", mock_agentic_entity, 
                files=["file1.py", "file2.py"]
            )
            
            assert result == ""
            assert mock_delete.call_count == 2

    @pytest.mark.asyncio
    async def test_delete_files_no_files(self, service, mock_agentic_entity):
        """Test file deletion with no files specified."""
        result = await service.delete_files("tech_id", mock_agentic_entity, files=[])
        
        assert result == "No files specified for deletion"

    @pytest.mark.asyncio
    async def test_save_entity_templates_success(self, service, mock_chat_entity):
        """Test successful entity templates saving."""
        entity_data = {
            "entities": [
                {
                    "entity_name": "User",
                    "entity_data_example": {"id": 1, "name": "test"}
                },
                {
                    "entity_name": "Product",
                    "entity_data_example": {"id": 1, "title": "test"}
                }
            ]
        }
        
        with patch('common.utils.utils.get_project_file_name', return_value="/path/to/design.json"), \
             patch('aiofiles.open', mock_open(read_data=str(entity_data).replace("'", '"'))), \
             patch('json.loads', return_value=entity_data), \
             patch('common.utils.utils._save_file', new_callable=AsyncMock) as mock_save, \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):
            
            result = await service.save_entity_templates("tech_id", mock_chat_entity)
            
            assert result == "Entity templates saved successfully"
            assert mock_save.call_count == 2

    @pytest.mark.asyncio
    async def test_save_entity_templates_missing_entity_name(self, service, mock_chat_entity):
        """Test entity templates saving with missing entity name."""
        entity_data = {
            "entities": [
                {
                    "entity_data_example": {"id": 1, "name": "test"}
                }
            ]
        }
        
        with patch('common.utils.utils.get_project_file_name', return_value="/path/to/design.json"), \
             patch('aiofiles.open', mock_open(read_data=str(entity_data).replace("'", '"'))), \
             patch('json.loads', return_value=entity_data), \
             patch('common.utils.utils._save_file', new_callable=AsyncMock) as mock_save, \
             patch('common.utils.utils.get_repository_name', return_value="test_repo"):
            
            result = await service.save_entity_templates("tech_id", mock_chat_entity)
            
            assert result == "Entity templates saved successfully"
            mock_save.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_entity_templates_error(self, service, mock_chat_entity):
        """Test entity templates saving with error."""
        with patch('common.utils.utils.get_project_file_name', side_effect=Exception("Test error")):
            result = await service.save_entity_templates("tech_id", mock_chat_entity)
            
            assert "Error saving entity templates" in result
            assert mock_chat_entity.failed is True
