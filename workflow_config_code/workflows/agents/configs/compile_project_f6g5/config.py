"""
CompileProjectF6g5AgentConfig Configuration

Generated from config: workflow_configs/agents/configs/compile_project_f6g5/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.prompts.compile_project_f6g5.prompt import CompileProjectF6g5PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "model": {},
        "tools": [],
        "memory_tags": [
                "CompileProjectF6g5PromptConfig"
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": CompileProjectF6g5PromptConfig.get_name()
                }
        ],
        "input": {
                "local_fs": [
                        "src/main/java/com/java_template/prototype/project_compilation.log"
                ]
        },
        "output": {
                "local_fs": [
                        "src/main/java/com/java_template/prototype/project_compilation_output.json"
                ]
        },
        "response_format": {
                "name": "workflow_design_schema",
                "description": "workflow design schema",
                "schema": {
                        "type": "object",
                        "properties": {
                                "compilation_status": {
                                        "type": "string",
                                        "enum": [
                                                "SUCCESS",
                                                "FAILURE"
                                        ],
                                        "description": "Indicates whether the compilation succeeded or failed."
                                },
                                "files_with_errors": {
                                        "type": "array",
                                        "description": "List of files that contain compilation errors.",
                                        "items": {
                                                "type": "object",
                                                "properties": {
                                                        "file_path": {
                                                                "type": "string",
                                                                "description": "Path to the file that encountered errors."
                                                        },
                                                        "errors": {
                                                                "type": "array",
                                                                "description": "List of error messages for this file.",
                                                                "items": {
                                                                        "type": "string"
                                                                }
                                                        }
                                                },
                                                "required": [
                                                        "file_path",
                                                        "errors"
                                                ],
                                                "additionalProperties": False
                                        }
                                }
                        },
                        "required": [
                                "compilation_status",
                                "files_with_errors"
                        ],
                        "additionalProperties": False
                }
        }
}
