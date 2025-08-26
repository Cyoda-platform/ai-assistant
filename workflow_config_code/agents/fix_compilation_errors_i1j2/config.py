"""
FixCompilationErrorsI1j2AgentConfig Configuration

Configuration data for the fix compilation errors agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.fix_compilation_errors_i1j2.prompt import FixCompilationErrorsI1j2PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "jobs": [
            {
                "type": "agent",
                "publish": False,
                "model": {},
                "tools": [],
                "split_function": {
                    "name": "get_files_with_compilation_errors",
                    "split_parameter": "file_path",
                    "input_file": "src/main/java/com/java_template/prototype/project_compilation_output.json"
                },
                "memory_tags": [
                    "FixCompilationErrorsI1j2PromptConfig"
                ],
                "output": "{file_path}",
                "tool_choice": "auto",
                "max_iteration": 30,
                "approve": True,
                "input": {
                    "local_fs": [
                        "{file_path}",
                        "src/main/java/com/java_template/prototype/project_compilation_output.json"
                    ]
                },
                "messages": [
                    {
                        "role": "user",
                        "content_from_file": FixCompilationErrorsI1j2PromptConfig.get_name()
                    }
                ]
            }
        ]
    }
