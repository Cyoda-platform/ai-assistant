"""
FixCompilationErrorsI1j2AgentConfig Configuration

Generated from config: workflow_configs/agents/configs/fix_compilation_errors_i1j2/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable



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
                                        "src/main/java/com/java_template/application/entity",
                                        "src/main/java/com/java_template/prototype/project_compilation_output.json"
                                ]
                        },
                        "messages": [
                                {
                                        "role": "user",
                                        "content_from_file": "fix_compilation_errors_i1j2"
                                }
                        ]
                }
        ]
}
