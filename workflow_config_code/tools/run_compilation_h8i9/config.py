"""
RunCompilationH8i9ToolConfig Configuration

Configuration data for the run compilation tool.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.run_github_action_ozv1.tool import RunGithubActionOzv1ToolConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
            "name": "run_github_action",
            "description": "Triggers GitHub Actions compilation workflow for the Java project",
            "parameters": {
                "workflow_id": "build.yml",
                "owner": "Cyoda-platform",
                "option": "compile-only"
            }
        },
        "memory_tags": [
            "compile_project"
        ],
        "output": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/project_compilation.log"
            ]
        }

    }
