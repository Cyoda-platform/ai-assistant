"""
ProcessInitialQuestionCd33AgentConfig Configuration

Generated from config: workflow_configs/agents/process_initial_question_cd33/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_collaborator_to_default_repos_ffe7.tool import \
    AddCollaboratorToDefaultReposFfe7ToolConfig
from workflow_config_code.tools.get_cyoda_guidelines_c748.tool import GetCyodaGuidelinesC748ToolConfig
from workflow_config_code.tools.web_search_7e4b.tool import WebSearch7e4bToolConfig
from workflow_config_code.tools.read_link_c472.tool import ReadLinkC472ToolConfig
from workflow_config_code.tools.web_scrape_bc54.tool import WebScrapeBc54ToolConfig
from workflow_config_code.prompts.process_initial_question_f6f7.prompt import ProcessInitialQuestionF6f7PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "publish": True,
        "allow_anonymous_users": True,
        "model": {"model_name": "gpt-4.1-mini"},
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
            }
        ],
        "memory_tags": [
            "requirements_generation"
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": ProcessInitialQuestionF6f7PromptConfig.get_name()
            }
        ],
        "tool_choice": "auto",
        "max_iteration": 30,
        "approve": True
    }
