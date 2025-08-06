"""
DeleteFiles6818ToolConfig Configuration

Generated from config: workflow_configs/tools/delete_files_6818/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "delete_files",
                "description": "delete_files",
                "parameters": {
                        "files": [
                                "src/main/java/com/java_template/prototype/EntityControllerPrototypeWithoutProcessing.java"
                        ],
                        "directories": [
                                "src/main/java/com/java_template/application/workflow_prototypes"
                        ]
                }
        },
        "publish": False
}
