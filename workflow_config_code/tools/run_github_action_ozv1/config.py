"""
RunGithubActionOzv1ToolConfig Configuration

Configuration data for the GitHub action runner tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
            "name": "run_github_action",
            "description": "Run a GitHub Actions workflow and wait for completion with timeout. This is a high-level tool that triggers a workflow, monitors its progress, and returns the final result. Use this when you need to run a build, deployment, or other CI/CD process and get the final outcome.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "repository_name": {
                        "type": "string",
                        "description": "Repository name (e.g., 'java-client-template')",
                        "enum": [
                            "java-client-template"
                        ]
                    },
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID or filename (e.g., 'build.yml')",
                        "enum": [
                            "build.yml"
                        ]
                    },
                    "owner": {
                        "type": "string",
                        "description": "Repository owner (optional, uses config default if not provided)",
                        "enum": [
                            "Cyoda-platform"
                        ]
                    },
                    "git_branch": {
                        "type": "string",
                        "description": "Git reference - branch or tag (optional, defaults to 'main')"
                    },
                    "option": {
                        "type": "string",
                        "description": "Git option (optional, defaults to 'compile-only')",
                        "enum": [
                            "compile-only"
                        ]
                    }
                },
                "required": [
                    "repository_name",
                    "workflow_id",
                    "owner",
                    "git_branch",
                    "option"
                ],
                "additionalProperties": False
            }
        }
    }
