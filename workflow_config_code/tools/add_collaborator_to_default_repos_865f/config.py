"""
AddCollaboratorToDefaultRepos865fToolConfig Configuration

Generated from config: workflow_configs/tools/add_collaborator_to_default_repos_865f/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "add_collaborator_to_default_repos",
                "description": "Adds a user as collaborator to the default Cyoda repositories (quart-client-template, java-client-template). Use when user requests repository access, push rights, or to be added to repositories. The AI must extract the GitHub username from the user's request - cannot invent usernames.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "username": {
                                        "type": "string",
                                        "description": "GitHub username extracted from user's request. Must be provided by the user - AI cannot invent this."
                                }
                        },
                        "required": [
                                "username"
                        ],
                        "additionalProperties": False
                }
        }
}
