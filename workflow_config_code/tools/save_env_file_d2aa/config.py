"""
SaveEnvFileD2aaToolConfig Configuration

Generated from config: workflow_configs/tools/save_env_file_d2aa/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
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
