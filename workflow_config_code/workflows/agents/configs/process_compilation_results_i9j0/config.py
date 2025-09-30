"""
ProcessCompilationResultsI9j0AgentConfig Configuration

Generated from config: workflow_configs/agents/configs/process_compilation_results_i9j0/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.workflows.agents.tools.list_directory_files_1ab7.tool import ListDirectoryFiles1ab7ToolConfig
from workflow_config_code.workflows.agents.tools.read_file_2766.tool import ReadFile2766ToolConfig
from workflow_config_code.workflows.agents.prompts.process_compilation_results_i9j0.prompt import ProcessCompilationResultsI9j0PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": False,
        "approve": False,
        "model": {},
        "tools": [
                {
                        "name": AddApplicationResource3d0bToolConfig.get_tool_name()
                },
                {
                        "name": ListDirectoryFiles1ab7ToolConfig.get_tool_name()
                },
                {
                        "name": ReadFile2766ToolConfig.get_tool_name()
                }
        ],
        "memory_tags": [
                "generate_processors_and_criteria"
        ],
        "input": {
                "local_fs": [
                        "src/main/java/com/java_template/prototype/project_compilation.log"
                ]
        },
        "messages": [
                {
                        "role": "user",
                        "content_from_file": ProcessCompilationResultsI9j0PromptConfig.get_name()
                }
        ]
}
