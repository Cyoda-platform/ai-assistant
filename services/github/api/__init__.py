"""
GitHub API Module

Handles all GitHub REST API interactions including:
- Workflow operations
- Repository management
- Collaborator management
"""

from services.github.api.client import GitHubAPIClient
from services.github.api.workflows import WorkflowOperations
from services.github.api.repositories import RepositoryOperations
from services.github.api.collaborators import CollaboratorOperations

__all__ = [
    "GitHubAPIClient",
    "WorkflowOperations",
    "RepositoryOperations",
    "CollaboratorOperations",
]

