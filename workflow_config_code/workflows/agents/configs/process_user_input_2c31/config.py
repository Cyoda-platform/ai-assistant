"""
ProcessUserInput2c31AgentConfig Configuration

Generated from config: workflow_configs/agents/configs/process_user_input_2c31/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.tools.add_collaborator_to_default_repos_ffe7.tool import AddCollaboratorToDefaultReposFfe7ToolConfig
from workflow_config_code.workflows.agents.tools.get_cyoda_guidelines_c748.tool import GetCyodaGuidelinesC748ToolConfig
from workflow_config_code.workflows.agents.tools.web_search_7e4b.tool import WebSearch7e4bToolConfig
from workflow_config_code.workflows.agents.tools.read_link_c472.tool import ReadLinkC472ToolConfig
from workflow_config_code.workflows.agents.tools.web_scrape_bc54.tool import WebScrapeBc54ToolConfig
from workflow_config_code.workflows.agents.tools.finish_discussion_66e9.tool import FinishDiscussion66e9ToolConfig
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
        "tools": [
                {
                        "name": AddCollaboratorToDefaultReposFfe7ToolConfig.get_tool_name()
                },
                {
                        "name": GetCyodaGuidelinesC748ToolConfig.get_tool_name()
                },
                {
                        "name": WebSearch7e4bToolConfig.get_tool_name()
                },
                {
                        "name": ReadLinkC472ToolConfig.get_tool_name()
                },
                {
                        "name": WebScrapeBc54ToolConfig.get_tool_name()
                },
                {
                        "name": FinishDiscussion66e9ToolConfig.get_tool_name()
                }
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": ProcessUserInput23bdPromptConfig.get_name()
                }
        ],
        "input": {
                "local_fs": [
                        "src/main/resources/functional_requirements/user_requirement.md"
                ]
        },
        "output": {
                "local_fs": [
                        "src/main/resources/functional_requirements/user_requirement_additional_info.md"
                ]
        },
        "tool_choice": "auto",
        "max_iteration": 30,
        "approve": True
}
