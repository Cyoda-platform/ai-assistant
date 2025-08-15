import json
import logging
import time
import zipfile
import io
from typing import Optional, Dict, Any
import aiohttp

from common.config import const
from common.config.config import config
from common.utils.utils import send_put_request
from entity.chat.chat import ChatEntity
from tools.base_service import BaseWorkflowService


logger = logging.getLogger(__name__)


class GitHubOperationsService(BaseWorkflowService):
    """
    Service responsible for GitHub operations including
    adding collaborators, managing repositories, and other GitHub API interactions.
    """

    async def add_collaborator(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Invite or add a collaborator to a GitHub repository.
        Now uses configuration defaults with username as the only required parameter.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including:
                - username: GitHub username of the collaborator to invite (REQUIRED)
                - owner: Repository owner (optional, uses config default)
                - repo: Repository name (optional, uses first default repo)
                - permission: Permission level (optional, uses config default)

        Returns:
            Success message or error message
        """
        try:
            # Validate required parameters - only username is required now
            is_valid, error_msg = await self._validate_required_params(
                params, ["username"]
            )
            if not is_valid:
                return error_msg

            # Check if GitHub token is configured
            if not config.GH_TOKEN:
                return "Error: GH_TOKEN not configured in environment variables"

            # Extract parameters with configuration defaults
            username = params.get("username")
            owner = config.GH_DEFAULT_OWNER
            repos = config.GH_DEFAULT_REPOS
            permission = config.GH_DEFAULT_PERMISSION

            # Make the API request using custom GitHub API call
            success_msgs = []
            for repo in repos:
                response = await self._make_github_api_request(
                    method="PUT",
                    path=f"repos/{owner}/{repo}/collaborators/{username}",
                    data={"permission": permission}
                )

                # GitHub API returns different status codes:
                # 201: Invitation sent (user not yet a collaborator)
                # 204: User added as collaborator (user already has access)
                if response is not None:
                    success_msg = f"Success: Invited user '{username}' to repository '{owner}/{repo}' with '{permission}' permission. Please check your email to accept the invitation."
                    self.logger.info(success_msg)
                    success_msgs.append(success_msg)
                else:
                    error_msg = f"Failed to add collaborator '{username}' to repository '{owner}/{repo}'"
                    self.logger.error(error_msg)
                    return error_msg

            return json.dumps(success_msgs)

        except Exception as e:
            return self._handle_error(entity, e, f"Error adding collaborator: {e}")

    async def get_repository_info(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Get information about a GitHub repository.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including:
                - owner: Repository owner (username or organization)
                - repository_name: Repository name
                
        Returns:
            Repository information or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["owner", "repository_name"]
            )
            if not is_valid:
                return error_msg

            # Check if GitHub token is configured
            if not config.GH_TOKEN:
                return "Error: GH_TOKEN not configured in environment variables"

            # Extract parameters
            owner = params.get("owner")
            repo = params.get("repository_name")

            # This would require implementing a GET request method
            # For now, return a placeholder message
            return f"Repository info for {owner}/{repo} - Feature to be implemented"

        except Exception as e:
            return self._handle_error(entity, e, f"Error getting repository info: {e}")

    async def _make_github_api_request(self, method: str, path: str, data: Optional[dict] = None) -> Optional[dict]:
        """
        Make a GitHub API request with proper headers and error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path (without base URL)
            data: Request data for POST/PUT requests

        Returns:
            Response data or None if request failed

        Raises:
            Exception: If request fails
        """
        import httpx

        url = f"https://api.github.com/{path}"
        headers = {
            "Authorization": f"Bearer {config.GH_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "PUT":
                    response = await client.put(url, json=data, headers=headers)
                elif method.upper() == "GET":
                    response = await client.get(url, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data, headers=headers)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

            # GitHub API returns 201 for invitation sent, 204 for collaborator added
            if response.status_code in (200, 201, 204):
                self.logger.info(f"GitHub API {method} request to {url} successful (status: {response.status_code})")
                try:
                    return response.json() if response.content else {}
                except:
                    return {}
            else:
                error_msg = f"GitHub API request failed (status {response.status_code}): {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

        except httpx.RequestError as e:
            error_msg = f"GitHub API request error: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            self.logger.error(f"Unexpected error in GitHub API request: {e}")
            raise

    async def trigger_github_workflow(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Trigger a GitHub Actions workflow and return the run ID.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including:
                - owner: Repository owner (optional, uses config default)
                - repository_name: Repository name (required)
                - workflow_id: Workflow ID or filename (required)
                - ref: Git reference for workflow dispatch (optional, defaults to 'main')
                - git_branch: Branch to build (optional, defaults to technical_id)
                - inputs: Additional workflow inputs as dict (optional)
                - tracker_id: Unique tracker ID for monitoring (optional, auto-generated if not provided)

        Returns:
            JSON string with run_id and tracker_id, or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["repository_name", "workflow_id"]
            )
            if not is_valid:
                return error_msg

            # Check if GitHub token is configured
            if not config.GH_TOKEN:
                return "Error: GH_TOKEN not configured in environment variables"

            # Extract parameters with defaults
            owner = params.get("owner", config.GH_DEFAULT_OWNER)
            repo = params["repository_name"]
            workflow_id = params.get("workflow_id")
            ref = params.get("ref", "main")  # Use "main" as default ref for workflow dispatch
            git_branch = params.get("git_branch", technical_id)  # The actual branch to build
            inputs = params.get("inputs", {})
            tracker_id = params.get("tracker_id", f"tracker_{int(time.time())}")

            # Prepare inputs according to the expected format
            if isinstance(inputs, dict):
                # Add the branch parameter for the workflow
                inputs["branch"] = git_branch
                inputs["tracker_id"] = tracker_id
                # Add build_type if not specified
                if "build_type" not in inputs:
                    inputs["build_type"] = "compile-only"
            else:
                inputs = {
                    "branch": git_branch,
                    "tracker_id": tracker_id,
                    "build_type": "compile-only"
                }

            # Trigger the workflow with the correct structure
            dispatch_data = {
                "ref": ref,
                "inputs": inputs
            }

            response = await self._make_github_api_request(
                method="POST",
                path=f"repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
                data=dispatch_data
            )

            if response is not None:
                # Wait a moment for the run to appear
                await self._wait_for_run_to_appear()

                # Find the run by tracker ID
                run_id = await self._find_run_by_tracker_id(owner, repo, workflow_id, tracker_id)

                if run_id:
                    result = {
                        "status": "success",
                        "message": f"Workflow '{workflow_id}' triggered successfully",
                        "run_id": run_id,
                        "tracker_id": tracker_id,
                        "repository": f"{owner}/{repo}",
                        "ref": ref
                    }
                    self.logger.info(f"Workflow triggered: {result}")
                    return json.dumps(result)
                else:
                    return f"Error: Workflow triggered but run not found with tracker_id: {tracker_id}"
            else:
                return f"Error: Failed to trigger workflow '{workflow_id}' in repository '{owner}/{repo}'"

        except Exception as e:
            return self._handle_error(entity, e, f"Error triggering GitHub workflow: {e}")

    async def monitor_workflow_run(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Monitor a GitHub Actions workflow run and return its status.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including:
                - owner: Repository owner (optional, uses config default)
                - repository_name: Repository name (required)
                - run_id: Workflow run ID (required)

        Returns:
            JSON string with run status information, or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["repository_name", "run_id"]
            )
            if not is_valid:
                return error_msg

            # Check if GitHub token is configured
            if not config.GH_TOKEN:
                return "Error: GH_TOKEN not configured in environment variables"

            # Extract parameters
            owner = params.get("owner", config.GH_DEFAULT_OWNER)
            repo = params.get("repository_name")
            run_id = params.get("run_id")

            # Get run status
            response = await self._make_github_api_request(
                method="GET",
                path=f"repos/{owner}/{repo}/actions/runs/{run_id}"
            )

            if response:
                result = {
                    "run_id": response.get("id"),
                    "status": response.get("status"),
                    "conclusion": response.get("conclusion"),
                    "html_url": response.get("html_url"),
                    "workflow_name": response.get("name"),
                    "head_branch": response.get("head_branch"),
                    "created_at": response.get("created_at"),
                    "updated_at": response.get("updated_at"),
                    "repository": f"{owner}/{repo}"
                }
                self.logger.info(f"Workflow run status: {result}")
                return json.dumps(result)
            else:
                return f"Error: Failed to get status for run ID '{run_id}' in repository '{owner}/{repo}'"

        except Exception as e:
            return self._handle_error(entity, e, f"Error monitoring GitHub workflow run: {e}")

    async def get_workflow_run_status(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Get the current status of a GitHub Actions workflow run.
        This is a simplified version of monitor_workflow_run that returns just the status.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including:
                - owner: Repository owner (optional, uses config default)
                - repository_name: Repository name (required)
                - run_id: Workflow run ID (required)

        Returns:
            Status string or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["repository_name", "run_id"]
            )
            if not is_valid:
                return error_msg

            # Check if GitHub token is configured
            if not config.GH_TOKEN:
                return "Error: GH_TOKEN not configured in environment variables"

            # Extract parameters
            owner = params.get("owner", config.GH_DEFAULT_OWNER)
            repo = params.get("repository_name")
            run_id = params.get("run_id")

            # Get run status
            response = await self._make_github_api_request(
                method="GET",
                path=f"repos/{owner}/{repo}/actions/runs/{run_id}"
            )

            if response:
                status = response.get("status", "unknown")
                conclusion = response.get("conclusion")

                if conclusion:
                    return f"{status} - {conclusion}"
                else:
                    return status
            else:
                return f"Error: Failed to get status for run ID '{run_id}'"

        except Exception as e:
            return self._handle_error(entity, e, f"Error getting workflow run status: {e}")

    async def run_github_action(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Run a GitHub Actions workflow and wait for completion with timeout.
        This is a high-level method that triggers a workflow, monitors it, and returns the final result.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including:
                - owner: Repository owner (optional, uses config default)
                - repository_name: Repository name (required)
                - workflow_id: Workflow ID or filename (required)
                - git_branch: Git reference (branch/tag) (optional, defaults to 'main')
                - inputs: Workflow inputs as dict (optional)
                - timeout_minutes: Timeout in minutes (optional, defaults to 2)

        Returns:
            JSON string with final workflow result, or error/timeout message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["workflow_id"]
            )
            if not is_valid:
                return error_msg

            params["repository_name"] = entity.workflow_cache.get(const.REPOSITORY_NAME_PARAM, "JAVA")
            params["git_branch"] = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            # Check if GitHub token is configured
            if not config.GH_TOKEN:
                return "Error: GH_TOKEN not configured in environment variables"

            # Extract parameters with defaults
            timeout_minutes = params.get("timeout_minutes", 2)
            timeout_seconds = timeout_minutes * 60

            self.logger.info(f"Starting GitHub Action run with {timeout_minutes} minute timeout")

            # Step 1: Trigger the workflow
            trigger_result = await self.trigger_github_workflow(technical_id, entity, **params)

            # Check if trigger was successful
            if not trigger_result.startswith('{"status": "success"'):
                return f"Failed to trigger workflow: {trigger_result}"

            # Parse trigger result to get run_id
            trigger_data = json.loads(trigger_result)
            run_id = trigger_data.get("run_id")
            tracker_id = trigger_data.get("tracker_id")

            if not run_id:
                return "Error: Failed to get run_id from workflow trigger"

            self.logger.info(f"Workflow triggered successfully. Run ID: {run_id}, Tracker ID: {tracker_id}")

            # Step 2: Wait for completion with timeout
            import asyncio
            start_time = time.time()
            poll_interval = 10  # Poll every 10 seconds

            while True:
                elapsed_time = time.time() - start_time

                # Check timeout
                if elapsed_time >= timeout_seconds:
                    timeout_result = {
                        "status": "timeout",
                        "message": f"Workflow did not complete within {timeout_minutes} minutes",
                        "run_id": run_id,
                        "tracker_id": tracker_id,
                        "elapsed_time_seconds": int(elapsed_time),
                        "timeout_seconds": timeout_seconds
                    }
                    self.logger.warning(f"Workflow timeout: {timeout_result}")
                    return json.dumps(timeout_result)

                # Get current status
                owner = params.get("owner", config.GH_DEFAULT_OWNER)
                repo = params.get("repository_name")
                status_result = await self.get_workflow_run_status(
                    technical_id, entity,
                    repository_name=repo,
                    run_id=run_id,
                    owner=owner
                )

                self.logger.debug(f"Workflow status check: {status_result}")

                # Check if workflow completed
                if "completed" in status_result.lower():
                    # Get detailed final result
                    final_result = await self.monitor_workflow_run(
                        technical_id, entity,
                        repository_name=repo,
                        run_id=run_id,
                        owner=owner
                    )

                    final_data = json.loads(final_result)
                    conclusion = final_data.get("conclusion", "unknown")

                    # Prepare comprehensive result
                    result = {
                        "status": "completed",
                        "conclusion": conclusion,
                        "success": conclusion == "success",
                        "run_id": run_id,
                        "tracker_id": tracker_id,
                        "elapsed_time_seconds": int(elapsed_time),
                        "html_url": final_data.get("html_url"),
                        "workflow_name": final_data.get("workflow_name"),
                        "repository": final_data.get("repository"),
                        "head_branch": final_data.get("head_branch"),
                        "created_at": final_data.get("created_at"),
                        "updated_at": final_data.get("updated_at")
                    }

                    # Always retrieve logs for completed workflows (success or failure)
                    self.logger.info(f"Workflow completed with conclusion '{conclusion}', retrieving logs...")
                    logs_content = await self._download_workflow_logs(owner, repo, run_id)
                    if logs_content:
                        self.logger.info(f"Retrieved {len(logs_content)} characters of logs")
                        # Return just the extracted log content as text
                        return logs_content
                    else:
                        self.logger.warning("Failed to retrieve workflow logs")
                        return "Failed to retrieve logs"

                # Wait before next poll
                await asyncio.sleep(poll_interval)

        except Exception as e:
            return self._handle_error(entity, e, f"Error running GitHub action: {e}")

    async def _wait_for_run_to_appear(self, wait_seconds: int = 5) -> None:
        """
        Wait for a workflow run to appear in the GitHub API.

        Args:
            wait_seconds: Number of seconds to wait
        """
        import asyncio
        await asyncio.sleep(wait_seconds)

    async def _find_run_by_tracker_id(self, owner: str, repo: str, workflow_id: str, tracker_id: str) -> Optional[str]:
        """
        Find a workflow run by tracker ID in the display_title or logs.

        Args:
            owner: Repository owner
            repo: Repository name
            workflow_id: Workflow ID or filename
            tracker_id: Tracker ID to search for

        Returns:
            Run ID if found, None otherwise
        """
        try:
            # Get recent workflow runs
            response = await self._make_github_api_request(
                method="GET",
                path=f"repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs?per_page=10"
            )

            if response and "workflow_runs" in response:
                for run in response["workflow_runs"]:
                    run_id = run.get("id")
                    if not run_id:
                        continue

                    # First check display_title for tracker_id
                    display_title = run.get("display_title", "")
                    if tracker_id in display_title:
                        return str(run_id)

                    # Get detailed run information to check inputs
                    run_details = await self._make_github_api_request(
                        method="GET",
                        path=f"repos/{owner}/{repo}/actions/runs/{run_id}"
                    )

                    if run_details:
                        # Check inputs for tracker_id
                        if "inputs" in run_details:
                            inputs = run_details.get("inputs", {})
                            if inputs.get("tracker_id") == tracker_id:
                                return str(run_id)

                        # Check logs for tracker_id in summary
                        if await self._check_logs_for_tracker_id(owner, repo, run_id, tracker_id):
                            return str(run_id)

            return None

        except Exception as e:
            self.logger.error(f"Error finding run by tracker ID: {e}")
            return None

    async def get_workflow_logs(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Retrieve GitHub Actions workflow logs.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including:
                - owner: Repository owner (optional, uses config default)
                - repository_name: Repository name (required)
                - run_id: Workflow run ID (required)

        Returns:
            JSON string with logs content or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["repository_name", "run_id"]
            )
            if not is_valid:
                return error_msg

            # Check if GitHub token is configured
            if not config.GH_TOKEN:
                return "Error: GH_TOKEN not configured in environment variables"

            # Extract parameters
            owner = params.get("owner", config.GH_DEFAULT_OWNER)
            repo = params.get("repository_name")
            run_id = params.get("run_id")

            # Get logs
            logs_content = await self._download_workflow_logs(owner, repo, run_id)

            if logs_content:
                result = {
                    "run_id": run_id,
                    "repository": f"{owner}/{repo}",
                    "logs": logs_content
                }
                return json.dumps(result)
            else:
                return f"Error: Failed to retrieve logs for run ID '{run_id}' in repository '{owner}/{repo}'"

        except Exception as e:
            return self._handle_error(entity, e, f"Error getting workflow logs: {e}")

    async def get_enhanced_workflow_logs(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Get enhanced workflow logs with additional debugging information.
        This method provides more detailed logging and troubleshooting info.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including:
                - owner: Repository owner (optional, uses config default)
                - repository_name: Repository name (required)
                - run_id: Workflow run ID (required)

        Returns:
            Enhanced logs content with debugging info or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["repository_name", "run_id"]
            )
            if not is_valid:
                return error_msg

            # Check if GitHub token is configured
            if not config.GH_TOKEN:
                return "Error: GH_TOKEN not configured in environment variables"

            # Extract parameters
            owner = params.get("owner", config.GH_DEFAULT_OWNER)
            repo = params.get("repository_name")
            run_id = params.get("run_id")

            # Get basic run info first
            run_info = await self._make_github_api_request(
                method="GET",
                path=f"repos/{owner}/{repo}/actions/runs/{run_id}"
            )

            info_section = ""
            if run_info:
                info_section = f"""=== WORKFLOW RUN INFO ===
Run ID: {run_info.get('id')}
Status: {run_info.get('status')}
Conclusion: {run_info.get('conclusion')}
Workflow: {run_info.get('name')}
Branch: {run_info.get('head_branch')}
Created: {run_info.get('created_at')}
Updated: {run_info.get('updated_at')}
URL: {run_info.get('html_url')}

"""

            # Get logs
            logs_content = await self._download_workflow_logs(owner, repo, run_id)

            if logs_content:
                return f"{info_section}=== EXTRACTED LOGS ===\n{logs_content}"
            else:
                return f"{info_section}=== ERROR ===\nFailed to retrieve workflow logs"

        except Exception as e:
            return self._handle_error(entity, e, f"Error getting enhanced workflow logs: {e}")

    async def get_workflow_enhancement_suggestions(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Provide suggestions for enhancing GitHub workflow to capture comprehensive logs.

        Returns:
            Suggestions for improving workflow log capture
        """
        suggestions = """
=== GITHUB WORKFLOW ENHANCEMENT SUGGESTIONS ===

To capture comprehensive build logs, enhance your .github/workflows/*.yml file with:

1. **Enable verbose Gradle output:**
   ```yaml
   - name: Build with Gradle
     run: |
       ./gradlew build --info --stacktrace --no-daemon
       # Alternative: use --debug for even more verbose output
   ```

2. **Capture all output streams:**
   ```yaml
   - name: Build with full logging
     run: |
       ./gradlew build --info --stacktrace 2>&1 | tee build.log
       cat build.log
   ```

3. **Set Gradle logging properties:**
   ```yaml
   - name: Configure Gradle logging
     run: |
       echo "org.gradle.logging.level=info" >> gradle.properties
       echo "org.gradle.console=plain" >> gradle.properties
   ```

4. **Add step to show build output:**
   ```yaml
   - name: Show build results
     if: always()
     run: |
       echo "=== BUILD OUTPUT ==="
       find . -name "*.log" -exec cat {} \\;
       echo "=== GRADLE DAEMON LOGS ==="
       find ~/.gradle/daemon -name "*.log" -exec cat {} \\;
   ```

5. **Upload logs as artifacts:**
   ```yaml
   - name: Upload build logs
     if: always()
     uses: actions/upload-artifact@v3
     with:
       name: build-logs
       path: |
         **/*.log
         ~/.gradle/daemon/**/*.log
   ```

6. **For compilation errors, add:**
   ```yaml
   - name: Compile with detailed output
     run: |
       ./gradlew compileJava --info --stacktrace --continue
   ```

The current GitHub Actions log API may not capture all console output if the workflow
doesn't explicitly redirect it. The above enhancements ensure all build output is
captured in the GitHub Actions logs.
"""
        return suggestions

    async def _download_workflow_logs(self, owner: str, repo: str, run_id: str) -> Optional[str]:
        """
        Download and extract GitHub Actions workflow logs.

        Args:
            owner: Repository owner
            repo: Repository name
            run_id: Workflow run ID

        Returns:
            Combined logs content or None if failed
        """
        try:
            headers = {
                "Authorization": f"Bearer {config.GH_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "AI-Assistant"
            }

            async with aiohttp.ClientSession() as session:
                # First request to get the redirect URL
                async with session.get(
                    f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs",
                    headers=headers,
                    allow_redirects=False
                ) as response:
                    if response.status == 302:
                        # Follow the redirect to download the zip file
                        download_url = response.headers.get('Location')
                        if download_url:
                            async with session.get(download_url) as download_response:
                                if download_response.status == 200:
                                    # Read the zip content
                                    zip_content = await download_response.read()

                                    # Extract and combine log files
                                    combined_logs = []
                                    with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                                        self.logger.info(f"Found {len(zip_file.namelist())} files in log zip: {zip_file.namelist()}")
                                        for file_name in sorted(zip_file.namelist()):
                                            if file_name.endswith('.txt'):
                                                with zip_file.open(file_name) as log_file:
                                                    log_content = log_file.read().decode('utf-8', errors='ignore')
                                                    self.logger.info(f"Extracted {len(log_content)} characters from {file_name}")
                                                    combined_logs.append(f"=== {file_name} ===\n{log_content}\n")

                                    total_content = "\n".join(combined_logs) if combined_logs else None
                                    if total_content:
                                        self.logger.info(f"Total combined log content: {len(total_content)} characters")
                                    return total_content

            return None

        except Exception as e:
            self.logger.error(f"Error downloading workflow logs: {e}")
            return None

    async def _check_logs_for_tracker_id(self, owner: str, repo: str, run_id: str, tracker_id: str) -> bool:
        """
        Check GitHub Actions logs for tracker ID in the summary.

        Args:
            owner: Repository owner
            repo: Repository name
            run_id: Workflow run ID
            tracker_id: Tracker ID to search for

        Returns:
            True if tracker_id found in logs, False otherwise
        """
        try:
            # GitHub logs endpoint returns a redirect to the actual download URL
            headers = {
                "Authorization": f"Bearer {config.GH_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "AI-Assistant"
            }

            async with aiohttp.ClientSession() as session:
                # First request to get the redirect URL
                async with session.get(
                    f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs",
                    headers=headers,
                    allow_redirects=False
                ) as response:
                    if response.status == 302:
                        # Follow the redirect to download the zip file
                        download_url = response.headers.get('Location')
                        if download_url:
                            async with session.get(download_url) as download_response:
                                if download_response.status == 200:
                                    # Read the zip content
                                    zip_content = await download_response.read()

                                    # Extract and search through log files
                                    with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                                        for file_name in zip_file.namelist():
                                            if file_name.endswith('.txt'):
                                                with zip_file.open(file_name) as log_file:
                                                    log_content = log_file.read().decode('utf-8', errors='ignore')
                                                    if tracker_id in log_content:
                                                        return True

            return False

        except Exception as e:
            self.logger.error(f"Error checking logs for tracker ID: {e}")
            return False
