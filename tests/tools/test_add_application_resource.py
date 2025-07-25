"""
Tests for add_application_resource function in FileOperationsService.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

import common.config.const as const
from tools.file_operations_service import FileOperationsService
from entity.model import AgenticFlowEntity


class TestAddApplicationResource:
    """Test cases for add_application_resource function."""
    
    @pytest.fixture
    def service(self):
        """Create FileOperationsService instance with mocked dependencies."""
        mock_deps = {
            'workflow_helper_service': Mock(),
            'entity_service': Mock(),
            'cyoda_auth_service': Mock(),
            'workflow_converter_service': Mock(),
            'scheduler_service': Mock(),
            'data_service': Mock(),
            'dataset': None,
            'mock': True
        }
        return FileOperationsService(**mock_deps)
    
    @pytest.fixture
    def mock_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = Mock(spec=AgenticFlowEntity)
        entity.workflow_cache = {
            const.GIT_BRANCH_PARAM: "test_branch",
            "programming_language": "PYTHON"
        }
        entity.workflow_name = "test_workflow_python"
        entity.user_id = "test_user"
        entity.failed = False
        entity.error = None
        return entity
    
    @pytest.mark.asyncio
    async def test_add_application_resource_success(self, service, mock_entity):
        """Test successful addition of application resource."""
        with patch('tools.file_operations_service._save_file', new_callable=AsyncMock) as mock_save_file:
            with patch('tools.repository_resolver.resolve_repository_name', return_value="python_repo"):
                
                result = await service.add_application_resource(
                    technical_id="test_tech_id",
                    entity=mock_entity,
                    resource_path="config/settings.py",
                    file_contents="DEBUG = True\nSECRET_KEY = 'test'"
                )
                
                # Verify success message
                assert "Successfully added application resource" in result
                assert "config/settings.py" in result
                assert "32 characters" in result  # DEBUG = True\nSECRET_KEY = 'test' is 32 chars
                
                # Verify _save_file was called with correct parameters
                mock_save_file.assert_called_once()
                call_kwargs = mock_save_file.call_args.kwargs
                assert call_kwargs['_data'] == "DEBUG = True\nSECRET_KEY = 'test'"
                assert call_kwargs['item'] == "config/settings.py"
                assert call_kwargs['git_branch_id'] == "test_branch"
                assert call_kwargs['repository_name'] == "python_repo"
    
    @pytest.mark.asyncio
    async def test_add_application_resource_java_project(self, service):
        """Test adding resource to Java project."""
        java_entity = Mock(spec=AgenticFlowEntity)
        java_entity.workflow_cache = {
            const.GIT_BRANCH_PARAM: "java_branch",
            "programming_language": "JAVA"
        }
        java_entity.workflow_name = "test_workflow_java"
        java_entity.user_id = "test_user"
        java_entity.failed = False
        java_entity.error = None
        
        with patch('tools.file_operations_service._save_file', new_callable=AsyncMock) as mock_save_file:
            with patch('tools.repository_resolver.resolve_repository_name', return_value="java_repo"):
                
                result = await service.add_application_resource(
                    technical_id="test_tech_id",
                    entity=java_entity,
                    resource_path="src/main/resources/application.properties",
                    file_contents="server.port=8080\nspring.application.name=test-app"
                )
                
                assert "Successfully added application resource" in result
                assert "src/main/resources/application.properties" in result
                
                # Verify correct repository was used
                call_kwargs = mock_save_file.call_args.kwargs
                assert call_kwargs['repository_name'] == "java_repo"
    
    @pytest.mark.asyncio
    async def test_missing_required_parameters(self, service, mock_entity):
        """Test validation of required parameters."""
        # Test missing resource_path
        result = await service.add_application_resource(
            technical_id="test_tech_id",
            entity=mock_entity,
            file_contents="some content"
            # Missing resource_path
        )
        assert "Missing required parameters: resource_path" in result

        # Test missing file_contents
        result = await service.add_application_resource(
            technical_id="test_tech_id",
            entity=mock_entity,
            resource_path="config/test.py"
            # Missing file_contents
        )
        assert "Missing required parameters: file_contents" in result

        # Test missing both parameters
        result = await service.add_application_resource(
            technical_id="test_tech_id",
            entity=mock_entity
        )
        assert "Missing required parameters: resource_path, file_contents" in result
    
    @pytest.mark.asyncio
    async def test_invalid_resource_paths(self, service, mock_entity):
        """Test validation of resource paths."""
        test_cases = [
            ("../../../etc/passwd", "directory traversal"),
            ("/absolute/path/file.txt", "absolute path"),
            ("path/../other/file.txt", "path with .. in middle"),
        ]

        for invalid_path, description in test_cases:
            result = await service.add_application_resource(
                technical_id="test_tech_id",
                entity=mock_entity,
                resource_path=invalid_path,
                file_contents="content"
            )
            assert "Invalid resource path" in result, f"Failed to reject {description}: {invalid_path}"

        # Test empty path separately (it's caught by parameter validation)
        result = await service.add_application_resource(
            technical_id="test_tech_id",
            entity=mock_entity,
            resource_path="",
            file_contents="content"
        )
        assert "Missing required parameters: resource_path" in result
    
    @pytest.mark.asyncio
    async def test_valid_resource_paths(self, service, mock_entity):
        """Test acceptance of valid resource paths."""
        valid_paths = [
            "config/settings.py",
            "src/main/resources/application.properties",
            "templates/index.html",
            "static/css/style.css",
            "docs/README.md",
            "data/sample.json"
        ]
        
        with patch('tools.file_operations_service._save_file', new_callable=AsyncMock):
            with patch('tools.repository_resolver.resolve_repository_name', return_value="test_repo"):
                
                for valid_path in valid_paths:
                    result = await service.add_application_resource(
                        technical_id="test_tech_id",
                        entity=mock_entity,
                        resource_path=valid_path,
                        file_contents="test content"
                    )
                    assert "Successfully added application resource" in result, f"Failed to accept valid path: {valid_path}"
    
    @pytest.mark.asyncio
    async def test_different_file_contents(self, service, mock_entity):
        """Test handling of different file content types."""
        test_contents = [
            ("single line", "single line content"),
            ("line1\nline2\nline3", "multi-line content"),
            ('{"key": "value", "number": 123}', "JSON content"),
            ("# Comment\nkey=value\nother_key=other_value", "properties content"),
            ("a" * 10000, "large content")
        ]
        
        with patch('tools.file_operations_service._save_file', new_callable=AsyncMock) as mock_save_file:
            with patch('tools.repository_resolver.resolve_repository_name', return_value="test_repo"):
                
                for content, description in test_contents:
                    result = await service.add_application_resource(
                        technical_id="test_tech_id",
                        entity=mock_entity,
                        resource_path="test/file.txt",
                        file_contents=content
                    )
                    
                    assert "Successfully added application resource" in result, f"Failed for {description}"
                    assert f"({len(content)} characters)" in result
                    
                    # Verify content was passed correctly
                    call_kwargs = mock_save_file.call_args.kwargs
                    assert call_kwargs['_data'] == content

        # Test empty file contents separately (it's caught by parameter validation)
        result = await service.add_application_resource(
            technical_id="test_tech_id",
            entity=mock_entity,
            resource_path="test/empty.txt",
            file_contents=""
        )
        assert "Missing required parameters: file_contents" in result
    
    @pytest.mark.asyncio
    async def test_repository_resolution(self, service):
        """Test that repository resolution works correctly."""
        # Test Python entity
        python_entity = Mock(spec=AgenticFlowEntity)
        python_entity.workflow_cache = {
            const.GIT_BRANCH_PARAM: "python_branch",
            "programming_language": "PYTHON"
        }
        python_entity.workflow_name = "test_workflow_python"
        python_entity.failed = False
        python_entity.error = None
        
        with patch('tools.file_operations_service._save_file', new_callable=AsyncMock) as mock_save_file:
            with patch('tools.repository_resolver.resolve_repository_name') as mock_resolve:
                mock_resolve.return_value = "resolved_repo"
                
                await service.add_application_resource(
                    technical_id="test_tech_id",
                    entity=python_entity,
                    resource_path="test/file.py",
                    file_contents="print('hello')"
                )
                
                # Verify resolver was called with entity
                mock_resolve.assert_called_once_with(python_entity)
                
                # Verify resolved repository name was used
                call_kwargs = mock_save_file.call_args.kwargs
                assert call_kwargs['repository_name'] == "resolved_repo"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service, mock_entity):
        """Test error handling when _save_file fails."""
        with patch('tools.file_operations_service._save_file', new_callable=AsyncMock) as mock_save_file:
            with patch('tools.repository_resolver.resolve_repository_name', return_value="test_repo"):
                
                # Make _save_file raise an exception
                mock_save_file.side_effect = Exception("File system error")
                
                result = await service.add_application_resource(
                    technical_id="test_tech_id",
                    entity=mock_entity,
                    resource_path="test/file.txt",
                    file_contents="content"
                )
                
                assert "Error adding application resource" in result
                assert "File system error" in result
    
    @pytest.mark.asyncio
    async def test_git_branch_handling(self, service):
        """Test handling of different git branch scenarios."""
        # Test with git branch in workflow cache
        entity_with_branch = Mock(spec=AgenticFlowEntity)
        entity_with_branch.workflow_cache = {
            const.GIT_BRANCH_PARAM: "feature_branch",
            "programming_language": "PYTHON"
        }
        entity_with_branch.workflow_name = "test_workflow"
        entity_with_branch.failed = False
        entity_with_branch.error = None
        
        with patch('tools.file_operations_service._save_file', new_callable=AsyncMock) as mock_save_file:
            with patch('tools.repository_resolver.resolve_repository_name', return_value="test_repo"):
                
                await service.add_application_resource(
                    technical_id="tech_id_123",
                    entity=entity_with_branch,
                    resource_path="test/file.txt",
                    file_contents="content"
                )
                
                # Should use branch from workflow cache
                call_kwargs = mock_save_file.call_args.kwargs
                assert call_kwargs['git_branch_id'] == "feature_branch"
        
        # Test without git branch in workflow cache (should use technical_id)
        entity_without_branch = Mock(spec=AgenticFlowEntity)
        entity_without_branch.workflow_cache = {"programming_language": "PYTHON"}
        entity_without_branch.workflow_name = "test_workflow"
        entity_without_branch.failed = False
        entity_without_branch.error = None
        
        with patch('tools.file_operations_service._save_file', new_callable=AsyncMock) as mock_save_file:
            with patch('tools.repository_resolver.resolve_repository_name', return_value="test_repo"):
                
                await service.add_application_resource(
                    technical_id="fallback_tech_id",
                    entity=entity_without_branch,
                    resource_path="test/file.txt",
                    file_contents="content"
                )
                
                # Should use technical_id as fallback
                call_kwargs = mock_save_file.call_args.kwargs
                assert call_kwargs['git_branch_id'] == "fallback_tech_id"
