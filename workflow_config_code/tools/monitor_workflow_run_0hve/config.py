"""
MonitorWorkflowRun0hveToolConfig Configuration

Configuration data for the GitHub workflow monitoring tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "monitor_workflow_run",
                "description": "Monitor a GitHub Actions workflow run and get detailed status information. Use this to check the progress and results of a previously triggered workflow.",
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
                                        "description": "Workflow run ID to monitor"
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
