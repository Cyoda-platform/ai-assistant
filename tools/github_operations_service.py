import json
import logging
from typing import Optional

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
                params, ["owner", "repo"]
            )
            if not is_valid:
                return error_msg

            # Check if GitHub token is configured
            if not config.GH_TOKEN:
                return "Error: GH_TOKEN not configured in environment variables"

            # Extract parameters
            owner = params.get("owner")
            repo = params.get("repo")

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
