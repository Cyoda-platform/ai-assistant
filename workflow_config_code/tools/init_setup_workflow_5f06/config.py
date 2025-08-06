"""
InitSetupWorkflow5f06ToolConfig Configuration

Generated from config: workflow_configs/tools/init_setup_workflow_5f06/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "init_setup_workflow",
                "description": "init_setup_workflow",
                "parameters": {
                        "user_request": "Hello! Please help me start my new application.",
                        "programming_language": "JAVA"
                }
        },
        "publish": False
}
