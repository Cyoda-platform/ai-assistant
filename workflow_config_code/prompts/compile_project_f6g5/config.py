"""
CompileProjectF6g5PromptConfig Configuration

Configuration data for the compile project prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
You are provided with the compilation output from GitHub Actions. Analyze the output to determine if the project compiles successfully.

Return json with files that failed compilation and errors in the following format:
{ 
    "compilation_status": "SUCCESS" or "FAILURE",
    "files_with_errors": [
        {"file_path": "path/to/file1.java", "errors": ["error1", "error2"]},
        {"file_path": "path/to/file2.java", "errors": ["error3", "error4"]}
  ]
}
"""
