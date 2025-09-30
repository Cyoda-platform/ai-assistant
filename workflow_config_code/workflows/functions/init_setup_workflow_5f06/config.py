"""
InitSetupWorkflow5f06FunctionConfig Configuration

Generated from config: workflow_configs/functions/init_setup_workflow_5f06/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "init_setup_workflow",
                "description": "init_setup_workflow",
                "parameters": {
                        "user_request": "Hello! Please help me start my new application."
                }
        },
        "publish": False
}
