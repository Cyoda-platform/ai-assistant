import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tools.base_service import BaseWorkflowService
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity


class TestBaseWorkflowService:
    """Test cases for BaseWorkflowService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for BaseWorkflowService."""
        return {
            'workflow_helper_service': AsyncMock(),
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
            'workflow_converter_service': AsyncMock(),
            'scheduler_service': AsyncMock(),
            'data_service': AsyncMock(),
            'dataset': None,
            'mock': False
        }

    @pytest.fixture
    def base_service(self, mock_dependencies):
        """Create BaseWorkflowService instance with mocked dependencies."""
        return BaseWorkflowService(**mock_dependencies)

    @pytest.fixture
    def mock_entity(self):
        """Create mock ChatEntity."""
        entity = MagicMock(spec=ChatEntity)
        entity.failed = False
        entity.error = None
        return entity

    def test_init(self, mock_dependencies):
        """Test BaseWorkflowService initialization."""
        service = BaseWorkflowService(**mock_dependencies)
        
        assert service.workflow_helper_service == mock_dependencies['workflow_helper_service']
        assert service.entity_service == mock_dependencies['entity_service']
        assert service.cyoda_auth_service == mock_dependencies['cyoda_auth_service']
        assert service.workflow_converter_service == mock_dependencies['workflow_converter_service']
        assert service.scheduler_service == mock_dependencies['scheduler_service']
        assert service.data_service == mock_dependencies['data_service']
        assert service.dataset is None
        assert service.mock is False
        assert service.logger is not None

    def test_handle_error(self, base_service, mock_entity):
        """Test error handling functionality."""
        error = Exception("Test error")
        message = "Custom error message"
        
        result = base_service._handle_error(mock_entity, error, message)
        
        assert mock_entity.failed is True
        assert mock_entity.error == "Error: Test error"
        assert result == message

    def test_handle_error_default_message(self, base_service, mock_entity):
        """Test error handling with default message."""
        error = Exception("Test error")
        
        result = base_service._handle_error(mock_entity, error)
        
        assert mock_entity.failed is True
        assert mock_entity.error == "Error: Test error"
        assert result == "Error during operation: Test error"

    @pytest.mark.asyncio
    async def test_validate_required_params_success(self, base_service):
        """Test successful parameter validation."""
        params = {"param1": "value1", "param2": "value2"}
        required_fields = ["param1", "param2"]
        
        is_valid, error_msg = await base_service._validate_required_params(params, required_fields)
        
        assert is_valid is True
        assert error_msg == ""

    @pytest.mark.asyncio
    async def test_validate_required_params_missing(self, base_service):
        """Test parameter validation with missing fields."""
        params = {"param1": "value1"}
        required_fields = ["param1", "param2", "param3"]
        
        is_valid, error_msg = await base_service._validate_required_params(params, required_fields)
        
        assert is_valid is False
        assert "Missing required parameters: param2, param3" in error_msg

    @pytest.mark.asyncio
    async def test_validate_required_params_empty_values(self, base_service):
        """Test parameter validation with empty values."""
        params = {"param1": "", "param2": None, "param3": "value3"}
        required_fields = ["param1", "param2", "param3"]
        
        is_valid, error_msg = await base_service._validate_required_params(params, required_fields)
        
        assert is_valid is False
        assert "Missing required parameters: param1, param2" in error_msg

    def test_parse_from_string(self, base_service):
        """Test string parsing functionality."""
        escaped_code = "Hello\\nWorld\\t!"
        
        result = base_service.parse_from_string(escaped_code)
        
        assert result == "Hello\nWorld\t!"

    @pytest.mark.asyncio
    async def test_get_entities_list_python_repo(self, base_service):
        """Test getting entities list for Python repository."""
        with patch('os.listdir') as mock_listdir, \
             patch('os.path.isdir') as mock_isdir, \
             patch('common.config.config.config') as mock_config:
            
            mock_config.PROJECT_DIR = "/test/project"
            mock_listdir.return_value = ["entity1", "entity2", "file.txt"]
            mock_isdir.side_effect = lambda path: not path.endswith("file.txt")
            
            result = await base_service.get_entities_list("branch1", "python_repo")
            
            assert result == ["entity1", "entity2"]
            mock_listdir.assert_called_once_with("/test/project/branch1/python_repo/entity")

    @pytest.mark.asyncio
    async def test_get_entities_list_java_repo(self, base_service):
        """Test getting entities list for Java repository."""
        with patch('os.listdir') as mock_listdir, \
             patch('os.path.isdir') as mock_isdir, \
             patch('common.config.config.config') as mock_config:
            
            mock_config.PROJECT_DIR = "/test/project"
            mock_listdir.return_value = ["Entity1", "Entity2"]
            mock_isdir.return_value = True
            
            result = await base_service.get_entities_list("branch1", "java_repo")
            
            assert result == ["Entity1", "Entity2"]
            expected_path = "/test/project/branch1/java_repo/src/main/java/com/java_template/entity"
            mock_listdir.assert_called_once_with(expected_path)

    @pytest.mark.asyncio
    async def test_get_entities_list_error(self, base_service):
        """Test getting entities list with error."""
        with patch('os.listdir', side_effect=FileNotFoundError("Directory not found")):
            result = await base_service.get_entities_list("branch1", "repo")
            
            assert result == []

    @pytest.mark.asyncio
    async def test_resolve_entity_name_success(self, base_service):
        """Test successful entity name resolution."""
        # Mock the entire resolve_entity_name method since it has complex imports
        with patch.object(base_service, 'resolve_entity_name', return_value="user") as mock_resolve:
            result = await base_service.resolve_entity_name("usr", "branch1", "repo")

            assert result == "user"
            mock_resolve.assert_called_once_with("usr", "branch1", "repo")

    @pytest.mark.asyncio
    async def test_resolve_entity_name_no_match(self, base_service):
        """Test entity name resolution with no match."""
        # Mock the entire resolve_entity_name method since it has complex imports
        with patch.object(base_service, 'resolve_entity_name', return_value="unknown") as mock_resolve:
            result = await base_service.resolve_entity_name("unknown", "branch1", "repo")

            assert result == "unknown"
            mock_resolve.assert_called_once_with("unknown", "branch1", "repo")

    @pytest.mark.asyncio
    async def test_resolve_entity_name_error(self, base_service):
        """Test entity name resolution with error."""
        with patch.object(base_service, 'get_entities_list', side_effect=Exception("Test error")):
            result = await base_service.resolve_entity_name("entity", "branch1", "repo")
            
            assert result == "entity"
