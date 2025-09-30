"""
SaveEnvFileD2aaFunctionConfig Configuration

Generated from config: workflow_configs/functions/save_env_file_d2aa/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "save_env_file",
                "description": "save_env_file",
                "parameters": {
                        "filename": ".env.template"
                }
        },
        "publish": True
}
