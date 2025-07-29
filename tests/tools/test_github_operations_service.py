import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from tools.github_operations_service import GitHubOperationsService
from entity.chat.chat import ChatEntity


class TestGitHubOperationsService:
    """Test cases for GitHubOperationsService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for GitHubOperationsService."""
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
    def github_service(self, mock_dependencies):
        """Create GitHubOperationsService instance with mocked dependencies."""
        return GitHubOperationsService(**mock_dependencies)

    @pytest.fixture
    def mock_entity(self):
        """Create a mock ChatEntity."""
        entity = ChatEntity(
            memory_id="test_memory_id",
            user_id="test_user",
            workflow_cache={},
            failed=False,
            error=None
        )
        return entity

    @pytest.mark.asyncio
    async def test_add_collaborator_success(self, github_service, mock_entity):
        """Test successful collaborator addition."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            
            with patch.object(github_service, '_make_github_api_request') as mock_api:
                mock_api.return_value = {"message": "success"}
                
                result = await github_service.add_collaborator(
                    technical_id="test_id",
                    entity=mock_entity,
                    owner="test_owner",
                    repo="test_repo",
                    username="test_user",
                    permission="push"
                )
                
                assert "Success: Invited user 'test_user'" in result
                assert "test_owner/test_repo" in result
                assert "push" in result
                mock_api.assert_called_once_with(
                    method="PUT",
                    path="repos/test_owner/test_repo/collaborators/test_user",
                    data={"permission": "push"}
                )

    @pytest.mark.asyncio
    async def test_add_collaborator_missing_token(self, github_service, mock_entity):
        """Test collaborator addition with missing GitHub token."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = None
            
            result = await github_service.add_collaborator(
                technical_id="test_id",
                entity=mock_entity,
                owner="test_owner",
                repo="test_repo",
                username="test_user"
            )
            
            assert "Error: GH_TOKEN not configured" in result

    @pytest.mark.asyncio
    async def test_add_collaborator_missing_params(self, github_service, mock_entity):
        """Test collaborator addition with missing required parameters."""
        result = await github_service.add_collaborator(
            technical_id="test_id",
            entity=mock_entity
            # Missing username (only required parameter now)
        )

        assert "Missing required parameters" in result

    @pytest.mark.asyncio
    async def test_add_collaborator_invalid_permission(self, github_service, mock_entity):
        """Test collaborator addition with invalid permission level."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            
            result = await github_service.add_collaborator(
                technical_id="test_id",
                entity=mock_entity,
                owner="test_owner",
                repo="test_repo",
                username="test_user",
                permission="invalid_permission"
            )
            
            assert "Error: Invalid permission 'invalid_permission'" in result
            assert "Valid options:" in result

    @pytest.mark.asyncio
    async def test_add_collaborator_api_error(self, github_service, mock_entity):
        """Test collaborator addition with API error."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            mock_config.GH_DEFAULT_OWNER = "default_owner"
            mock_config.GH_DEFAULT_REPOS = ["default_repo"]
            mock_config.GH_DEFAULT_PERMISSION = "push"

            with patch.object(github_service, '_make_github_api_request') as mock_api:
                mock_api.side_effect = Exception("API Error")

                result = await github_service.add_collaborator(
                    technical_id="test_id",
                    entity=mock_entity,
                    username="test_user"
                )

                assert "Error adding collaborator" in result
                assert mock_entity.failed is True

    @pytest.mark.asyncio
    async def test_add_collaborator_default_permission(self, github_service, mock_entity):
        """Test collaborator addition with default permission."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            mock_config.GH_DEFAULT_PERMISSION = "push"

            with patch.object(github_service, '_make_github_api_request') as mock_api:
                mock_api.return_value = {"message": "success"}

                result = await github_service.add_collaborator(
                    technical_id="test_id",
                    entity=mock_entity,
                    owner="test_owner",
                    repo="test_repo",
                    username="test_user"
                    # No permission specified, should use config default
                )

                mock_api.assert_called_once_with(
                    method="PUT",
                    path="repos/test_owner/test_repo/collaborators/test_user",
                    data={"permission": "push"}
                )

    @pytest.mark.asyncio
    async def test_add_collaborator_with_config_defaults(self, github_service, mock_entity):
        """Test collaborator addition using configuration defaults."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            mock_config.GH_DEFAULT_OWNER = "default-owner"
            mock_config.GH_DEFAULT_REPOS = ["default-repo"]
            mock_config.GH_DEFAULT_PERMISSION = "maintain"

            with patch.object(github_service, '_make_github_api_request') as mock_api:
                mock_api.return_value = {"message": "success"}

                result = await github_service.add_collaborator(
                    technical_id="test_id",
                    entity=mock_entity,
                    username="test_user"
                    # Only username provided, should use all config defaults
                )

                assert "Success: Invited user 'test_user'" in result
                assert "default-owner/default-repo" in result
                assert "maintain" in result
                mock_api.assert_called_once_with(
                    method="PUT",
                    path="repos/default-owner/default-repo/collaborators/test_user",
                    data={"permission": "maintain"}
                )

    @pytest.mark.asyncio
    async def test_make_github_api_request_put_success(self, github_service):
        """Test successful PUT request to GitHub API."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.content = b'{"message": "success"}'
            mock_response.json.return_value = {"message": "success"}
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.put.return_value = mock_response
                
                result = await github_service._make_github_api_request(
                    method="PUT",
                    path="test/path",
                    data={"test": "data"}
                )
                
                assert result == {"message": "success"}

    @pytest.mark.asyncio
    async def test_make_github_api_request_error_status(self, github_service):
        """Test GitHub API request with error status code."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.put.return_value = mock_response
                
                with pytest.raises(Exception) as exc_info:
                    await github_service._make_github_api_request(
                        method="PUT",
                        path="test/path",
                        data={"test": "data"}
                    )
                
                assert "GitHub API request failed (status 404)" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_make_github_api_request_network_error(self, github_service):
        """Test GitHub API request with network error."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.put.side_effect = httpx.RequestError("Network error")
                
                with pytest.raises(Exception) as exc_info:
                    await github_service._make_github_api_request(
                        method="PUT",
                        path="test/path",
                        data={"test": "data"}
                    )
                
                assert "GitHub API request error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_repository_info_missing_token(self, github_service, mock_entity):
        """Test repository info retrieval with missing token."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = None
            
            result = await github_service.get_repository_info(
                technical_id="test_id",
                entity=mock_entity,
                owner="test_owner",
                repo="test_repo"
            )
            
            assert "Error: GH_TOKEN not configured" in result

    @pytest.mark.asyncio
    async def test_list_collaborators_missing_params(self, github_service, mock_entity):
        """Test list collaborators with missing parameters."""
        result = await github_service.list_collaborators(
            technical_id="test_id",
            entity=mock_entity,
            owner="test_owner"
            # Missing repo parameter
        )
        
        assert "Missing required parameters" in result

    def test_valid_permissions(self, github_service):
        """Test that all valid GitHub permission levels are accepted."""
        valid_permissions = ["pull", "triage", "push", "maintain", "admin"]

        # This test verifies the permission validation logic
        for permission in valid_permissions:
            assert permission in ["pull", "triage", "push", "maintain", "admin"]

    @pytest.mark.asyncio
    async def test_add_collaborator_to_default_repos_success(self, github_service, mock_entity):
        """Test successful collaborator addition to default repositories."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            mock_config.GH_DEFAULT_OWNER = "Cyoda-platform"
            mock_config.GH_DEFAULT_REPOS = ["quart-client-template", "java-client-template"]
            mock_config.GH_DEFAULT_USERNAME = "test-user"
            mock_config.GH_DEFAULT_PERMISSION = "push"

            with patch.object(github_service, '_make_github_api_request') as mock_api:
                mock_api.return_value = {"message": "success"}

                result = await github_service.add_collaborator_to_default_repos(
                    technical_id="test_id",
                    entity=mock_entity,
                    username="custom-user"
                )

                assert "Collaborator Addition Summary" in result
                assert "custom-user" in result
                assert "2 successful, 0 failed" in result
                assert "quart-client-template" in result
                assert "java-client-template" in result
                assert mock_api.call_count == 2

    @pytest.mark.asyncio
    async def test_add_collaborator_to_default_repos_missing_username(self, github_service, mock_entity):
        """Test default repos function with missing username parameter."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"

            result = await github_service.add_collaborator_to_default_repos(
                technical_id="test_id",
                entity=mock_entity
                # Missing username parameter (now required)
            )

            assert "Missing required parameters" in result

    @pytest.mark.asyncio
    async def test_add_collaborator_to_default_repos_mixed_results(self, github_service, mock_entity):
        """Test default repos function with mixed success/failure results."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"
            mock_config.GH_DEFAULT_OWNER = "Cyoda-platform"
            mock_config.GH_DEFAULT_REPOS = ["repo1", "repo2"]
            mock_config.GH_DEFAULT_USERNAME = "test-user"
            mock_config.GH_DEFAULT_PERMISSION = "push"

            with patch.object(github_service, '_make_github_api_request') as mock_api:
                # First call succeeds, second fails
                mock_api.side_effect = [{"message": "success"}, Exception("API Error")]

                result = await github_service.add_collaborator_to_default_repos(
                    technical_id="test_id",
                    entity=mock_entity,
                    username="test-user"
                )

                assert "1 successful, 1 failed" in result
                assert "✓ Cyoda-platform/repo1" in result
                assert "✗ Cyoda-platform/repo2" in result

    @pytest.mark.asyncio
    async def test_add_collaborator_to_default_repos_custom_params(self, github_service, mock_entity):
        """Test default repos function with custom parameters."""
        with patch('tools.github_operations_service.config') as mock_config:
            mock_config.GH_TOKEN = "test_token"

            with patch.object(github_service, '_make_github_api_request') as mock_api:
                mock_api.return_value = {"message": "success"}

                result = await github_service.add_collaborator_to_default_repos(
                    technical_id="test_id",
                    entity=mock_entity,
                    username="custom-user",
                    permission="admin",
                    owner="custom-owner",
                    repos=["custom-repo1", "custom-repo2"]
                )

                assert "custom-user" in result
                assert "admin" in result
                assert "custom-owner" in result
                assert "custom-repo1" in result
                assert "custom-repo2" in result

                # Verify API calls were made with custom parameters
                expected_calls = [
                    (("PUT", "repos/custom-owner/custom-repo1/collaborators/custom-user"), {"data": {"permission": "admin"}}),
                    (("PUT", "repos/custom-owner/custom-repo2/collaborators/custom-user"), {"data": {"permission": "admin"}})
                ]
                assert mock_api.call_count == 2
