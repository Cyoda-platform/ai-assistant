"""
Git operations module for local repository management.
Handles clone, pull, push, and other git commands.
Supports both public repositories (personal access token) and private repositories (GitHub App).
"""

import asyncio
import logging
import os
from typing import List, Optional

from common.config.config import config
from services.github.models.types import GitOperationResult, CloneOptions, PushOptions, PullOptions
from services.github.repository.url_parser import construct_repository_url, parse_repository_url
from services.github.auth.installation_token_manager import InstallationTokenManager

logger = logging.getLogger(__name__)


_git_operations_lock = asyncio.Lock()


class GitOperations:
    """Handles all local git command operations with dual-mode authentication."""

    def __init__(self, installation_id: Optional[int] = None):
        """Initialize git operations.

        Args:
            installation_id: GitHub App installation ID (for private repos)
        """
        self._lock = _git_operations_lock
        self.installation_id = installation_id
        self._installation_token_manager = None

        if installation_id:
            self._installation_token_manager = InstallationTokenManager()
            logger.info(f"Git operations initialized with installation ID: {installation_id}")

    async def _get_repository_url(
        self,
        repository_name: str,
        repository_url: Optional[str] = None
    ) -> str:
        """Get repository URL with authentication.

        Args:
            repository_name: Repository name (used for public repos)
            repository_url: Custom repository URL (used for private repos)

        Returns:
            Authenticated repository URL
        """
        # If custom URL provided (private repo), use installation token
        if repository_url:
            if self.installation_id and self._installation_token_manager:
                token = await self._installation_token_manager.get_installation_token(self.installation_id)
                url_info = parse_repository_url(repository_url)
                return url_info.to_authenticated_url(token)
            else:
                # Custom URL without installation ID - use as-is (might fail if private)
                logger.warning(f"Custom repository URL provided without installation ID: {repository_url}")
                return repository_url

        # Public repo - use config URL template
        return config.REPOSITORY_URL.format(repository_name=repository_name)

    async def clone_repository(
        self,
        git_branch_id: str,
        repository_name: str,
        base_branch: Optional[str] = None,
        repository_url: Optional[str] = None
    ) -> GitOperationResult:
        """Clone repository and create new branch.

        Args:
            git_branch_id: Branch ID to create
            repository_name: Repository name (should be JAVA_REPOSITORY_NAME or PYTHON_REPOSITORY_NAME from config)
            base_branch: Base branch to checkout (defaults to config.CLIENT_GIT_BRANCH)
            repository_url: Custom repository URL (for private repos)

        Returns:
            GitOperationResult with success status and message

        Note:
            The repository_name parameter MUST be the value from config.JAVA_REPOSITORY_NAME or
            config.PYTHON_REPOSITORY_NAME to ensure consistent directory naming regardless of the
            actual repository name in the URL. This is critical for scripts that reference the
            cloned directory.
        """
        async with self._lock:
            repo_url = await self._get_repository_url(repository_name, repository_url)

            # CRITICAL: Always use repository_name as the clone directory name
            # This ensures consistency regardless of the actual repository URL or repository name
            # The repository_name parameter should always be config.JAVA_REPOSITORY_NAME or
            # config.PYTHON_REPOSITORY_NAME, NOT the actual repository name from the URL
            clone_dir_name = repository_name
            clone_dir = f"{config.PROJECT_DIR}/{git_branch_id}/{clone_dir_name}"
            base_branch = base_branch or config.CLIENT_GIT_BRANCH

            logger.info(f"Cloning repository to: {clone_dir} (using directory name: {clone_dir_name})")

            if await self._repo_exists(clone_dir):
                await self._pull_internal(git_branch_id, clone_dir_name, repository_url)
                return GitOperationResult(
                    success=True,
                    message=f"Repository already exists at {clone_dir}, pulled latest changes"
                )

            if config.CLONE_REPO != "true":
                await asyncio.to_thread(os.makedirs, clone_dir, exist_ok=True)
                logger.info(f"Target directory '{clone_dir}' is created.")
                return GitOperationResult(
                    success=True,
                    message=f"Directory created at {clone_dir} (CLONE_REPO=false)"
                )

            # Clone with explicit target directory to ensure we use repository_name as the directory name
            # This is crucial: git clone <url> <directory> will clone into <directory> regardless of
            # the repository name in the URL
            clone_process = await asyncio.create_subprocess_exec(
                'git', 'clone', repo_url, clone_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await clone_process.communicate()

            if clone_process.returncode != 0:
                error_msg = f"Error during git clone: {stderr.decode()}"
                logger.error(error_msg)
                return GitOperationResult(success=False, message="Clone failed", error=error_msg)

            base_checkout_process = await asyncio.create_subprocess_exec(
                'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                'checkout', base_branch,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await base_checkout_process.communicate()

            if base_checkout_process.returncode != 0:
                error_msg = f"Error during git checkout of base branch '{base_branch}': {stderr.decode()}"
                logger.error(error_msg)
                return GitOperationResult(success=False, message="Base checkout failed", error=error_msg)

            checkout_process = await asyncio.create_subprocess_exec(
                'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                'checkout', '-b', str(git_branch_id),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await checkout_process.communicate()

            if checkout_process.returncode != 0:
                error_msg = f"Error during git checkout of new branch '{git_branch_id}': {stderr.decode()}"
                logger.error(error_msg)
                return GitOperationResult(success=False, message="Branch creation failed", error=error_msg)

            logger.info(f"Repository cloned to {clone_dir}")

            os.chdir(clone_dir)
            await self._set_upstream_tracking(git_branch_id)
            await self._run_git_config()
            await self._pull_internal(git_branch_id, clone_dir_name, repository_url)

            return GitOperationResult(
                success=True,
                message=f"Repository cloned successfully to {clone_dir}"
            )
    
    async def pull(
        self,
        git_branch_id: str,
        repository_name: str,
        merge_strategy: str = "recursive",
        repository_url: Optional[str] = None
    ) -> GitOperationResult:
        """Pull latest changes from remote.

        Args:
            git_branch_id: Branch ID
            repository_name: Repository name
            merge_strategy: Git merge strategy
            repository_url: Custom repository URL (for private repos)

        Returns:
            GitOperationResult with diff information
        """
        async with self._lock:
            return await self._pull_internal(git_branch_id, repository_name, repository_url, merge_strategy)
    
    async def _pull_internal(
        self,
        git_branch_id: str,
        repository_name: str,
        repository_url: Optional[str] = None,
        merge_strategy: str = "recursive"
    ) -> GitOperationResult:
        """Internal pull without lock."""
        # CRITICAL: Always use repository_name as the clone directory name
        # This ensures consistency regardless of the actual repository URL or repository name
        # The repository_name parameter should always be config.JAVA_REPOSITORY_NAME or
        # config.PYTHON_REPOSITORY_NAME, NOT the actual repository name from the URL
        clone_dir_name = repository_name
        clone_dir = f"{config.PROJECT_DIR}/{git_branch_id}/{clone_dir_name}"

        try:
            checkout_process = await asyncio.create_subprocess_exec(
                'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                'checkout', str(git_branch_id),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await checkout_process.communicate()

            if checkout_process.returncode != 0:
                error_msg = f"Error during git checkout: {stderr.decode()}"
                logger.error(error_msg)
                return GitOperationResult(success=False, message="Checkout failed", error=error_msg)

            fetch_process = await asyncio.create_subprocess_exec(
                'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                'fetch', 'origin',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            fetch_stdout, fetch_stderr = await fetch_process.communicate()

            if fetch_process.returncode != 0:
                error_msg = f"Error during git fetch: {fetch_stderr.decode()}"
                logger.error(error_msg)
                return GitOperationResult(success=False, message="Fetch failed", error=error_msg)

            diff_process = await asyncio.create_subprocess_exec(
                'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                'diff', f"origin/{str(git_branch_id)}", str(git_branch_id),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            diff_stdout, diff_stderr = await diff_process.communicate()

            if diff_process.returncode != 0:
                error_msg = f"Error during git diff: {diff_stderr.decode()}"
                logger.error(error_msg)
                return GitOperationResult(success=False, message="Diff failed", error=error_msg)

            diff_result = diff_stdout.decode()
            logger.info(f"Git diff (before pull): {diff_result}")

            if not diff_result.strip():
                logger.info("No changes to pull, skipping pull.")
                return GitOperationResult(
                    success=True,
                    message="No changes to pull",
                    had_changes=False,
                    diff=diff_result
                )

            pull_process = await asyncio.create_subprocess_exec(
                'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                'pull', '--strategy', merge_strategy, '--strategy-option=theirs', 'origin', str(git_branch_id),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            pull_stdout, pull_stderr = await pull_process.communicate()

            if pull_process.returncode != 0:
                error_msg = f"Error during git pull: {pull_stderr.decode()}"
                logger.error(error_msg)
                return GitOperationResult(success=False, message="Pull failed", error=error_msg)

            logger.info(f"Git pull successful: {pull_stdout.decode()}")

            return GitOperationResult(
                success=True,
                message="Pull successful",
                had_changes=True,
                diff=diff_result
            )

        except Exception as e:
            error_msg = f"Unexpected error during git pull: {e}"
            logger.error(error_msg)
            logger.exception(e)
            return GitOperationResult(success=False, message="Pull failed", error=error_msg)
    
    async def push(
        self,
        git_branch_id: str,
        repository_name: str,
        file_paths: List[str],
        commit_message: str,
        repository_url: Optional[str] = None
    ) -> GitOperationResult:
        """Push changes to remote repository.

        Args:
            git_branch_id: Branch ID
            repository_name: Repository name
            file_paths: List of file paths to add
            commit_message: Commit message
            repository_url: Custom repository URL (for private repos)

        Returns:
            GitOperationResult with success status
        """
        async with self._lock:
            await self._pull_internal(git_branch_id, repository_name, repository_url)

            # Always use repository_name as the clone directory name
            clone_dir_name = repository_name
            clone_dir = f"{config.PROJECT_DIR}/{git_branch_id}/{clone_dir_name}"

            try:
                checkout_process = await asyncio.create_subprocess_exec(
                    'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                    'checkout', str(git_branch_id),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await checkout_process.communicate()
                if checkout_process.returncode != 0:
                    error_msg = f"Error during git checkout: {stderr.decode()}"
                    logger.error(error_msg)
                    return GitOperationResult(success=False, message="Checkout failed", error=error_msg)

                for file_path in file_paths:
                    add_process = await asyncio.create_subprocess_exec(
                        'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                        'add', file_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await add_process.communicate()
                    if add_process.returncode != 0:
                        error_msg = f"Error during git add {file_path}: {stderr.decode()}"
                        logger.error(error_msg)
                        return GitOperationResult(success=False, message="Add failed", error=error_msg)

                commit_process = await asyncio.create_subprocess_exec(
                    'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                    'commit', '-m', f"{commit_message}: {git_branch_id}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await commit_process.communicate()
                if commit_process.returncode != 0:
                    error_msg = f"Error during git commit: {stderr.decode()}"
                    logger.error(error_msg)
                    return GitOperationResult(success=False, message="Commit failed", error=error_msg)

                push_process = await asyncio.create_subprocess_exec(
                    'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                    'push', '-u', 'origin', str(git_branch_id),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await push_process.communicate()
                if push_process.returncode != 0:
                    error_msg = f"Error during git push: {stderr.decode()}"
                    logger.error(error_msg)
                    return GitOperationResult(success=False, message="Push failed", error=error_msg)

                logger.info("Git push successful!")
                return GitOperationResult(success=True, message="Push successful")

            except Exception as e:
                error_msg = f"Unexpected error during git push: {e}"
                logger.error(error_msg)
                logger.exception(e)
                return GitOperationResult(success=False, message="Push failed", error=error_msg)

    async def repository_exists(self, git_branch_id: str, repository_name: str) -> bool:
        """Check if repository directory exists.

        Args:
            git_branch_id: Branch ID
            repository_name: Repository name

        Returns:
            True if repository exists
        """
        path = f"{config.PROJECT_DIR}/{git_branch_id}/{repository_name}"
        return await self._repo_exists(path)

    async def _repo_exists(self, path: str) -> bool:
        """Check if path exists."""
        return await asyncio.to_thread(os.path.exists, path)

    async def _run_git_config(self):
        """Configure git pull behavior."""
        process = await asyncio.create_subprocess_exec(
            "git", "config", "pull.rebase", "false", "--global",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise Exception(f"Command failed with error: {stderr.decode().strip()}")
        logger.info(f"Git config set: {stdout.decode().strip()}")

    async def _set_upstream_tracking(self, git_branch_id: str):
        """Set upstream tracking for branch.

        Args:
            git_branch_id: Branch ID
        """
        branch = git_branch_id
        process = await asyncio.create_subprocess_exec(
            "git", "branch", "--set-upstream-to", f"origin/{branch}", branch,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logger.error(f"Error setting upstream: {stderr.decode().strip()}")
        else:
            logger.info(f"Successfully set upstream tracking for branch {branch}.")

