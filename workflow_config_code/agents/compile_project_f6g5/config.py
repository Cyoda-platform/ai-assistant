"""
CompileProjectF6g5AgentConfig Configuration

Configuration data for the compile project agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.tools.run_github_action_ozv1.tool import RunGithubActionOzv1ToolConfig
from workflow_config_code.prompts.compile_project_f6g5.prompt import CompileProjectF6g5PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "model": {},
        "tools": [
            {
                "name": RunGithubActionOzv1ToolConfig.get_tool_name()
            },
            {
                "name": AddApplicationResource3d0bToolConfig.get_tool_name()
            }
        ],
        "memory_tags": [
            "compile_project"
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": CompileProjectF6g5PromptConfig.get_name()
            }
        ]
    }
