"""
GetWorkflowRunStatusFz6jToolConfig Configuration

Configuration data for the GitHub workflow run status tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "get_workflow_run_status",
                "description": "Get the current status of a GitHub Actions workflow run. Returns a simple status string like 'completed - success', 'in_progress', or 'completed - failure'. Use this for quick status checks.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "repo": {
                                        "type": "string",
                                        "description": "Repository name (e.g., 'java-client-template')"
                                },
                                "run_id": {
                                        "type": "string",
                                        "description": "Workflow run ID to check status for"
                                },
                                "owner": {
                                        "type": "string",
                                        "description": "Repository owner (optional, uses config default if not provided)"
                                }
                        },
                        "required": [
                                "repo",
                                "run_id"
                        ],
                        "additionalProperties": False
                }
        }
}
