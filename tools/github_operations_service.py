import json
import logging
import time
from typing import Optional, Dict, Any

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
                    success_msg = f"Success: Invited user '{username}' to repository '{owner}/{repo}' with '{permission}' permission."
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
                - repo: Repository name
                
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
                - repo: Repository name (required)
                - workflow_id: Workflow ID or filename (required)
                - ref: Git reference (branch/tag) (optional, defaults to 'main')
                - inputs: Workflow inputs as dict (optional)
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
            ref = params["git_branch"]
            inputs = params.get("inputs", {})
            tracker_id = params.get("tracker_id", f"tracker_{int(time.time())}")

            # Add tracker_id to inputs for tracking
            if isinstance(inputs, dict):
                inputs["tracker_id"] = tracker_id
            else:
                inputs = {"tracker_id": tracker_id}

            # Trigger the workflow
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
                - repo: Repository name (required)
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
                - repo: Repository name (required)
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
                params, ["repository_name", "workflow_id"]
            )
            if not is_valid:
                return error_msg

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
                    repo=repo,
                    run_id=run_id,
                    owner=owner
                )

                self.logger.debug(f"Workflow status check: {status_result}")

                # Check if workflow completed
                if "completed" in status_result.lower():
                    # Get detailed final result
                    final_result = await self.monitor_workflow_run(
                        technical_id, entity,
                        repo=repo,
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

                    if conclusion == "success":
                        self.logger.info(f"Workflow completed successfully: {result}")
                    else:
                        self.logger.warning(f"Workflow completed with conclusion '{conclusion}': {result}")

                    return json.dumps(result)

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
        Find a workflow run by tracker ID in the inputs.

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
                    # Check if this run has our tracker_id in the inputs
                    run_id = run.get("id")
                    if run_id:
                        # Get detailed run information to check inputs
                        run_details = await self._make_github_api_request(
                            method="GET",
                            path=f"repos/{owner}/{repo}/actions/runs/{run_id}"
                        )

                        if run_details and "inputs" in run_details:
                            inputs = run_details.get("inputs", {})
                            if inputs.get("tracker_id") == tracker_id:
                                return str(run_id)

            return None

        except Exception as e:
            self.logger.error(f"Error finding run by tracker ID: {e}")
            return None
