"""
EditGeneralApplicationToolConfig Configuration

Generated from config: workflow_configs/agents/tools/edit_general_application/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
            "name": "edit_general_application",
            "description": """Launches workflow to edit/update an existing application. Use this when the user wants to modify, update, or continue working on an existing application.

CRITICAL: Git branch is REQUIRED. Ask the user explicitly or find it in chat history. Never default to 'main' branch.

CRITICAL: repository_type determines configuration:
- For PUBLIC repositories: Set repository_type='public', repository_url='', installation_id=''
- For PRIVATE repositories: Set repository_type='private' and MUST provide both repository_url and installation_id

When user says "public" or "none" for installation_id, use repository_type='public' with empty strings for repository_url and installation_id.""",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "git_branch": {
                        "type": "string",
                        "description": "The git branch where the application code exists (e.g., '35ac697a-636e-11b2-8aa9-be91bf237df2' or 'feature/xyz'). NEVER use 'main'."
                    },
                    "user_request": {
                        "type": "string",
                        "description": "The exact editing/update requirement from the user, without modification."
                    },
                    "programming_language": {
                        "type": "string",
                        "enum": [
                            "JAVA",
                            "PYTHON"
                        ],
                        "description": "Programming language of the application."
                    },
                    "repository_type": {
                        "type": "string",
                        "enum": [
                            "public",
                            "private"
                        ],
                        "description": "Type of repository: 'public' for Cyoda templates or 'private' for user's forked repository."
                    },
                    "repository_url": {
                        "type": "string",
                        "description": "GitHub repository URL (e.g., 'https://github.com/username/repo'). Use empty string \"\" for public repositories. REQUIRED for private repositories."
                    },
                    "installation_id": {
                        "type": "string",
                        "description": "GitHub App installation ID. Use empty string \"\" for public repositories. REQUIRED for private repositories."
                    }
                },
                "required": [
                    "user_request",
                    "git_branch",
                    "programming_language",
                    "repository_url",
                    "installation_id",
                    "repository_type"
                ],
                "additionalProperties": False
            }
        }
    }
