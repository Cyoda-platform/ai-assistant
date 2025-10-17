"""
Tests for GitHub models and types.
"""

import pytest
from services.github.models.types import (
    GitHubPermission,
    WorkflowStatus,
    WorkflowConclusion,
    ProgrammingLanguage,
    GitOperationResult,
    RepositoryInfo,
    WorkflowRunInfo,
    BranchInfo,
    CollaboratorInfo,
    GitConfig,
    CloneOptions,
    PushOptions,
    PullOptions,
)


class TestEnums:
    """Test enum types."""
    
    def test_github_permission_values(self):
        assert GitHubPermission.PULL.value == "pull"
        assert GitHubPermission.PUSH.value == "push"
        assert GitHubPermission.ADMIN.value == "admin"
        assert GitHubPermission.MAINTAIN.value == "maintain"
        assert GitHubPermission.TRIAGE.value == "triage"
    
    def test_workflow_status_values(self):
        assert WorkflowStatus.QUEUED.value == "queued"
        assert WorkflowStatus.IN_PROGRESS.value == "in_progress"
        assert WorkflowStatus.COMPLETED.value == "completed"
    
    def test_workflow_conclusion_values(self):
        assert WorkflowConclusion.SUCCESS.value == "success"
        assert WorkflowConclusion.FAILURE.value == "failure"
        assert WorkflowConclusion.CANCELLED.value == "cancelled"
        assert WorkflowConclusion.SKIPPED.value == "skipped"
    
    def test_programming_language_values(self):
        assert ProgrammingLanguage.PYTHON.value == "python"
        assert ProgrammingLanguage.JAVA.value == "java"


class TestGitOperationResult:
    """Test GitOperationResult dataclass."""
    
    def test_success_result(self):
        result = GitOperationResult(
            success=True,
            message="Operation successful"
        )
        assert result.success is True
        assert result.message == "Operation successful"
        assert result.had_changes is None
        assert result.diff is None
        assert result.error is None
    
    def test_failure_result(self):
        result = GitOperationResult(
            success=False,
            message="Operation failed",
            error="Error details"
        )
        assert result.success is False
        assert result.message == "Operation failed"
        assert result.error == "Error details"
    
    def test_result_with_changes(self):
        result = GitOperationResult(
            success=True,
            message="Changes detected",
            had_changes=True,
            diff="+ new line\n- old line"
        )
        assert result.success is True
        assert result.had_changes is True
        assert result.diff == "+ new line\n- old line"


class TestRepositoryInfo:
    """Test RepositoryInfo dataclass."""
    
    def test_repository_info_creation(self):
        repo = RepositoryInfo(
            name="test-repo",
            owner="test-owner",
            full_name="test-owner/test-repo",
            url="https://github.com/test-owner/test-repo",
            default_branch="main",
            private=False
        )
        assert repo.name == "test-repo"
        assert repo.owner == "test-owner"
        assert repo.full_name == "test-owner/test-repo"
        assert repo.url == "https://github.com/test-owner/test-repo"
        assert repo.default_branch == "main"
        assert repo.private is False
        assert repo.description is None
    
    def test_repository_info_with_description(self):
        repo = RepositoryInfo(
            name="test-repo",
            owner="test-owner",
            full_name="test-owner/test-repo",
            url="https://github.com/test-owner/test-repo",
            default_branch="main",
            private=True,
            description="Test repository"
        )
        assert repo.description == "Test repository"
        assert repo.private is True


class TestWorkflowRunInfo:
    """Test WorkflowRunInfo dataclass."""
    
    def test_workflow_run_info_creation(self):
        run = WorkflowRunInfo(
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
        assert run.run_id == 12345
        assert run.workflow_id == 67890
        assert run.status == WorkflowStatus.COMPLETED
        assert run.conclusion == WorkflowConclusion.SUCCESS
        assert run.html_url == "https://github.com/owner/repo/actions/runs/12345"
        assert run.head_branch == "main"
        assert run.head_sha == "abc123"
    
    def test_workflow_run_info_in_progress(self):
        run = WorkflowRunInfo(
            run_id=12345,
            workflow_id=67890,
            status=WorkflowStatus.IN_PROGRESS,
            conclusion=None,
            html_url="https://github.com/owner/repo/actions/runs/12345",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:01:00Z",
            head_branch="feature",
            head_sha="def456"
        )
        assert run.status == WorkflowStatus.IN_PROGRESS
        assert run.conclusion is None


class TestBranchInfo:
    """Test BranchInfo dataclass."""

    def test_branch_info_creation(self):
        branch = BranchInfo(
            name="feature-branch",
            sha="abc123def456",
            protected=False,
            repository_name="test-repo"
        )
        assert branch.name == "feature-branch"
        assert branch.sha == "abc123def456"
        assert branch.protected is False
        assert branch.repository_name == "test-repo"

    def test_branch_info_protected(self):
        branch = BranchInfo(
            name="main",
            sha="xyz789",
            protected=True,
            repository_name="test-repo"
        )
        assert branch.name == "main"
        assert branch.protected is True


class TestCollaboratorInfo:
    """Test CollaboratorInfo dataclass."""
    
    def test_collaborator_info_creation(self):
        collab = CollaboratorInfo(
            username="john-doe",
            permission=GitHubPermission.PUSH,
            repository="test-repo",
            owner="test-owner"
        )
        assert collab.username == "john-doe"
        assert collab.permission == GitHubPermission.PUSH
        assert collab.repository == "test-repo"
        assert collab.owner == "test-owner"


class TestGitConfig:
    """Test GitConfig dataclass."""

    def test_git_config_creation(self):
        config = GitConfig(
            user_name="John Doe",
            user_email="john@example.com"
        )
        assert config.user_name == "John Doe"
        assert config.user_email == "john@example.com"
        assert config.pull_rebase is False

    def test_git_config_with_rebase(self):
        config = GitConfig(
            user_name="Jane Doe",
            user_email="jane@example.com",
            pull_rebase=True
        )
        assert config.pull_rebase is True


class TestCloneOptions:
    """Test CloneOptions dataclass."""

    def test_clone_options_defaults(self):
        options = CloneOptions(
            repository_name="test-repo",
            branch_id="test-branch"
        )
        assert options.repository_name == "test-repo"
        assert options.branch_id == "test-branch"
        assert options.base_branch == "main"
        assert options.create_new_branch is True

    def test_clone_options_custom(self):
        options = CloneOptions(
            repository_name="test-repo",
            branch_id="test-branch",
            base_branch="develop",
            create_new_branch=False
        )
        assert options.base_branch == "develop"
        assert options.create_new_branch is False


class TestPushOptions:
    """Test PushOptions dataclass."""

    def test_push_options_defaults(self):
        options = PushOptions(
            branch_id="test-branch",
            repository_name="test-repo",
            commit_message="Test commit"
        )
        assert options.branch_id == "test-branch"
        assert options.repository_name == "test-repo"
        assert options.commit_message == "Test commit"
        assert options.files_to_add is None
        assert options.add_all is False

    def test_push_options_custom(self):
        options = PushOptions(
            branch_id="test-branch",
            repository_name="test-repo",
            commit_message="Test commit",
            files_to_add=["file1.py", "file2.py"],
            add_all=True
        )
        assert options.files_to_add == ["file1.py", "file2.py"]
        assert options.add_all is True


class TestPullOptions:
    """Test PullOptions dataclass."""
    
    def test_pull_options_defaults(self):
        options = PullOptions(
            branch_id="test-branch",
            repository_name="test-repo"
        )
        assert options.branch_id == "test-branch"
        assert options.repository_name == "test-repo"
        assert options.strategy == "recursive"
        assert options.strategy_option == "theirs"

    def test_pull_options_custom(self):
        options = PullOptions(
            branch_id="test-branch",
            repository_name="test-repo",
            strategy="ours",
            strategy_option="ours"
        )
        assert options.strategy == "ours"
        assert options.strategy_option == "ours"

