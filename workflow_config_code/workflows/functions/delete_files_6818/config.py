"""
DeleteFiles6818FunctionConfig Configuration

Generated from config: workflow_configs/functions/delete_files_6818/function.json
Configuration data for the function.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get function configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "delete_files",
                "description": "delete_files",
                "parameters": {
                        "files": [
                                "src/main/java/com/java_template/prototype/EntityControllerPrototypeWithoutProcessing.java",
                                "__init__.py"
                        ],
                        "directories": [
                                "src/main/java/com/java_template/application/workflow_prototypes"
                        ]
                }
        },
        "publish": False
}
