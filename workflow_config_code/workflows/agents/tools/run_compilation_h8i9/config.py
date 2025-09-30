"""
RunCompilationH8i9ToolConfig Configuration

Generated from config: workflow_configs/agents/tools/run_compilation_h8i9/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "publish": False,
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
