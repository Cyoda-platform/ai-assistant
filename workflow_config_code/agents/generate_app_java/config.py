"""
GenerateProcessorsAndCriteriaE5f4AgentConfig Configuration

Configuration data for the generate processors and criteria agent.
"""

from typing import Any, Dict, Callable

from workflow_config_code.prompts.generate_app_java.prompt import GenerateAppJavaPromptConfig
from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.tools.extract_workflow_components_k2l3.tool import ExtractWorkflowComponentsK2l3ToolConfig
from workflow_config_code.prompts.generate_processors_and_criteria_e5f4.prompt import GenerateProcessorsAndCriteriaE5f4PromptConfig
from workflow_config_code.tools.validate_workflow_processors.tool import ValidateWorkflowProcessorsToolConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "agent",
        "agent_type": "auggie",
        "script_path": "workflow/scripts/auggie_example.sh",
        "prompt": GenerateAppJavaPromptConfig.get_config(),
        "model": "sonnet4"
    }
