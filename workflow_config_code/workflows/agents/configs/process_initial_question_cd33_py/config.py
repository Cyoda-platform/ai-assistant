"""
ProcessInitialQuestionCd33PyAgentConfig Configuration

Generated from config: workflow_configs/agents/configs/process_initial_question_cd33_py/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.prompts.process_user_input_23bd.prompt import ProcessUserInput23bdPromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "allow_anonymous_users": True,
        "model": {
                "model_name": "gpt-4o-mini"
        },
        "memory_tags": [
                "process_initial_requirement"
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": ProcessUserInput23bdPromptConfig.get_name()
                }
        ],
        "input": {
                "local_fs": [
                        "application/resources/functional_requirements/user_requirement.md"
                ]
        },
        "max_iteration": 30,
        "approve": True
}
