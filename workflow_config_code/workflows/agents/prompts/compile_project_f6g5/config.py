"""
CompileProjectF6g5PromptConfig Configuration

Generated from config: workflow_configs/agents/prompts/compile_project_f6g5/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """You are provided with the compilation output from GitHub Actions. 
Analyze the output to determine if the project compiles successfully.

Return json with files that failed compilation and errors in the following format:
{ 
    "compilation_status": "SUCCESS" or "FAILURE",
    "files_with_errors": [
        {"file_path": "path/to/file1.java", "errors": ["error1", "error2"]},
        {"file_path": "path/to/file2.java", "errors": ["error3", "error4"]}
  ]
}
file_path can only be in 'src/main/java/com/java_template/application' or 'src/test/java/com/java_template/application/processor'. 

Exclude file paths that start with 'src/main/java/com/java_template/common'. This is a common directory for utility classes and should not be considered as part of the project's main source code.
There can be no errors in files starting with 'src/main/java/com/java_template/common'.
Errors can be only in files starting with 'src/main/java/com/java_template/application' or 'src/test/java/com/java_template/application/processor'."""
