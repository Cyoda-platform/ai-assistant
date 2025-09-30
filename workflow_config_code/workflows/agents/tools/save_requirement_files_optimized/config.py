"""
SaveRequirementFilesOptimizedToolConfig Configuration

Generated from config: workflow_configs/agents/tools/save_requirement_files_optimized/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "save_requirement_files_optimized",
                "description": "Initialises ai service",
                "parameters": {
                        "JAVA": "src/main/resources/functional_requirements",
                        "PYTHON": "application/resources/functional_requirements"
                }
        },
        "allow_anonymous_users": True
}
