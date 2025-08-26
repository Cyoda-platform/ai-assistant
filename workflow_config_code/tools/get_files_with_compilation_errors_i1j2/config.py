"""
GetFilesWithCompilationErrorsI1j2ToolConfig Configuration

Configuration data for the split function tool that extracts file paths from compilation output.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
            "name": "get_files_with_compilation_errors",
            "description": "Split function that parses project_compilation_output.json and returns file paths with compilation errors for parallel processing.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Path to the compilation output JSON file"
                    }
                },
                "required": [
                    "input_file"
                ],
                "additionalProperties": False
            }
        }
    }
