"""
Tests for main GitHubService facade.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.github import GitHubService
from services.github.models.types import GitOperationResult, GitHubPermission


class TestGitHubService:
    """Test GitHubService facade."""
    
    def test_service_initialization_default(self):
        with patch('services.github.api.client.config') as mock_config:
            mock_config.GITHUB_API_TOKEN = "test-token"
            mock_config.GH_DEFAULT_OWNER = "test-owner"

            service = GitHubService()
            assert service.api_client is not None
            assert service.workflows is not None
            assert service.repositories is not None
            assert service.collaborators is not None
            assert service.git is not None
            assert service.branches is not None
            assert service.credentials is not None
    
    def test_service_initialization_custom(self):
        service = GitHubService(token="custom-token", owner="custom-owner")
        assert service.api_client.token == "custom-token"
        assert service.api_client.owner == "custom-owner"
    
    @pytest.mark.asyncio
    async def test_clone_repository(self):
        service = GitHubService()
        
        expected_result = GitOperationResult(
            success=True,
            message="Repository cloned successfully"
        )
        
        with patch.object(service.git, 'clone_repository', new_callable=AsyncMock) as mock_clone:
            mock_clone.return_value = expected_result
            
            result = await service.clone_repository("test-branch", "test-repo")
            
            mock_clone.assert_called_once_with("test-branch", "test-repo", None)
            assert result.success is True
            assert result.message == "Repository cloned successfully"
    
    @pytest.mark.asyncio
    async def test_pull_changes(self):
        service = GitHubService()
        
        expected_result = GitOperationResult(
            success=True,
            message="Changes pulled successfully",
            had_changes=True
        )
        
        with patch.object(service.git, 'pull', new_callable=AsyncMock) as mock_pull:
            mock_pull.return_value = expected_result
            
            result = await service.pull_changes("test-branch", "test-repo")

            mock_pull.assert_called_once_with("test-branch", "test-repo", "recursive")
            assert result.success is True
            assert result.had_changes is True
    
    @pytest.mark.asyncio
    async def test_push_changes(self):
        service = GitHubService()
        
        expected_result = GitOperationResult(
            success=True,
            message="Changes pushed successfully"
        )
        
        with patch.object(service.git, 'push', new_callable=AsyncMock) as mock_push:
            mock_push.return_value = expected_result
            
            result = await service.push_changes(
                "test-branch",
                "test-repo",
                ["file1.py", "file2.py"],
                "Test commit"
            )
            
            mock_push.assert_called_once()
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_repository_exists(self):
        service = GitHubService()
        
        with patch.object(service.git, 'repository_exists', new_callable=AsyncMock) as mock_exists:
            mock_exists.return_value = True
            
            result = await service.repository_exists("test-branch", "test-repo")
            
            mock_exists.assert_called_once_with("test-branch", "test-repo")
            assert result is True
    
    @pytest.mark.asyncio
    async def test_trigger_workflow(self):
        service = GitHubService()
        
        expected_result = {
            "status": "success",
            "run_id": 12345,
            "tracker_id": "test-tracker"
        }
        
        with patch.object(service.workflows, 'trigger_workflow', new_callable=AsyncMock) as mock_trigger:
            mock_trigger.return_value = expected_result
            
            result = await service.trigger_workflow(
                "test-repo",
                "build.yml",
                inputs={"branch": "main"}
            )
            
            mock_trigger.assert_called_once()
            assert result["status"] == "success"
            assert result["run_id"] == 12345
    
    @pytest.mark.asyncio
    async def test_monitor_workflow(self):
        service = GitHubService()
        
        from services.github.models.types import WorkflowRunInfo, WorkflowStatus, WorkflowConclusion
        
        expected_result = WorkflowRunInfo(
            run_id=12345,
            workflow_id=67890,
            status=WorkflowStatus.COMPLETED,
            conclusion=WorkflowConclusion.SUCCESS,
            html_url="https://github.com/owner/repo/actions/runs/12345",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:05:00Z",
            head_branch="main",
            head_sha="abc123"
        )
        
        with patch.object(service.workflows, 'monitor_workflow_run', new_callable=AsyncMock) as mock_monitor:
            mock_monitor.return_value = expected_result
            
            result = await service.monitor_workflow("test-repo", 12345)
            
            mock_monitor.assert_called_once()
            assert result.run_id == 12345
            assert result.status == WorkflowStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_add_collaborator(self):
        service = GitHubService()
        
        from services.github.models.types import CollaboratorInfo
        
        expected_result = CollaboratorInfo(
            username="john-doe",
            permission=GitHubPermission.PUSH,
            repository="test-repo",
            owner="test-owner"
        )
        
        with patch.object(service.collaborators, 'add_collaborator', new_callable=AsyncMock) as mock_add:
            mock_add.return_value = expected_result
            
            result = await service.add_collaborator(
                "john-doe",
                "test-repo",
                GitHubPermission.PUSH
            )
            
            mock_add.assert_called_once()
            assert result.username == "john-doe"
            assert result.permission == GitHubPermission.PUSH
    
    def test_resolve_repository_name(self):
        service = GitHubService()
        
        entity = MagicMock()
        entity.workflow_cache = {}
        entity.workflow_name = "test_workflow"
        
        with patch('services.github.github_service.resolve_repository_name') as mock_resolve:
            mock_resolve.return_value = "test-repo"
            
            result = service.resolve_repository_name(entity, "python")
            
            mock_resolve.assert_called_once_with(entity, "python")
            assert result == "test-repo"
    
    def test_get_repository_config(self):
        service = GitHubService()
        
        with patch('services.github.github_service.RepositoryConfig') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.from_name.return_value = mock_config
            
            result = service.get_repository_config("test-repo")

            mock_config_class.from_name.assert_called_once_with("test-repo", None)
            assert result == mock_config
    
    @pytest.mark.asyncio
    async def test_get_repository_info(self):
        service = GitHubService()
        
        from services.github.models.types import RepositoryInfo
        
        expected_result = RepositoryInfo(
            name="test-repo",
            owner="test-owner",
            full_name="test-owner/test-repo",
            url="https://github.com/test-owner/test-repo",
            default_branch="main",
            private=False
        )
        
        with patch.object(service.repositories, 'get_repository', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = expected_result
            
            result = await service.get_repository_info("test-repo")
            
            mock_get.assert_called_once_with("test-repo", None)
            assert result.name == "test-repo"
            assert result.default_branch == "main"

