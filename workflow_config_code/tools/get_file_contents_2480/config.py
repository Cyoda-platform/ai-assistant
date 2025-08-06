"""
GetFileContents2480ToolConfig Configuration

Generated from config: workflow_configs/tools/get_file_contents_2480/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "get_file_contents",
                "description": "Get file contents by path to review existing code structure",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "file_path": {
                                        "type": "string",
                                        "description": "Path to the file to read. Examples: 'src/main/java/com/java_template/prototype/EntityControllerPrototype.java', 'src/main/java/com/java_template/application/controller/Controller.java', 'src/main/java/com/java_template/application/entity/EntityName.java', 'src/main/java/com/java_template/application/processor/ProcessorName.java', 'src/main/java/com/java_template/application/criterion/CriteriaName.java'"
                                }
                        },
                        "required": [
                                "file_path"
                        ],
                        "additionalProperties": False
                }
        }
}
