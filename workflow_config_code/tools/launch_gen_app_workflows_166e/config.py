"""
LaunchGenAppWorkflows166eToolConfig Configuration

Generated from config: workflow_configs/tools/launch_gen_app_workflows_166e/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "launch_gen_app_workflows",
                "description": "register_workflow_with_app",
                "parameters": {
                        "dir_name": "src/main/java/com/java_template/application/entity",
                        "next_transition": "validate_app_quality"
                }
        },
        "publish": False
}
