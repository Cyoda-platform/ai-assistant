"""
TriggerGithubWorkflowNw3vToolConfig Configuration

Generated from config: workflow_configs/agents/tools/trigger_github_workflow_nw3v/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "trigger_github_workflow",
                "description": "Trigger a GitHub Actions workflow and monitor its execution. Use this to start automated builds, deployments, or other CI/CD processes. Returns run ID and tracker ID for monitoring.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "repo": {
                                        "type": "string",
                                        "description": "Repository name (e.g., 'java-client-template')"
                                },
                                "workflow_id": {
                                        "type": "string",
                                        "description": "Workflow ID or filename (e.g., 'build.yml')"
                                },
                                "owner": {
                                        "type": "string",
                                        "description": "Repository owner (optional, uses config default if not provided)"
                                },
                                "ref": {
                                        "type": "string",
                                        "description": "Git reference - branch or tag (optional, defaults to 'main')"
                                },
                                "inputs": {
                                        "type": "object",
                                        "description": "Workflow inputs as key-value pairs (optional)",
                                        "additionalProperties": True
                                },
                                "tracker_id": {
                                        "type": "string",
                                        "description": "Unique tracker ID for monitoring (optional, auto-generated if not provided)"
                                }
                        },
                        "required": [
                                "repo",
                                "workflow_id"
                        ],
                        "additionalProperties": False
                }
        }
}
