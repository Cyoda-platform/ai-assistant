"""
ProcessInitialQuestionCd33AgentConfig Configuration

Generated from config: workflow_configs/agents/process_initial_question_cd33/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable

from workflow_config_code.prompts.process_user_input_23bd.prompt import ProcessUserInput23bdPromptConfig
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
        "model": {},
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
                "src/main/java/com/java_template/prototype/user_requirement.md"
            ]
        },
        "max_iteration": 30,
        "approve": True
    }
