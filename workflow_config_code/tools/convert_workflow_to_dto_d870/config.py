"""
ConvertWorkflowToDtoD870ToolConfig Configuration

Generated from config: workflow_configs/tools/convert_workflow_to_dto_d870/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "publish": False,
        "function": {
                "name": "convert_workflow_to_dto",
                "description": "convert_workflow_to_dto",
                "parameters": {
                        "workflow_file_name": "src/main/java/com/java_template/application/workflow/{EntityName}.json",
                        "output_file_name": "src/main/java/com/java_template/application/cyoda_dto/{EntityName}.json"
                }
        }
}
