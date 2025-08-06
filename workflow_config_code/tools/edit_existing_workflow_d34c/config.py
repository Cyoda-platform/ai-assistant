"""
EditExistingWorkflowD34cToolConfig Configuration

Generated from config: workflow_configs/tools/edit_existing_workflow_d34c/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "edit_existing_workflow",
                "description": "Launches workflow that is necessary to help the user edit an existing workflow/workflow json. Key factor is that an application already exists and the user explicitly asks to update a workflow (else default to edit_existing_app_design_additional_feature). if the user doesn't specify the branch, ask yourself.  Git branch is required. Ask the user explicitly or use the last branch from messages. Never default to main branch.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "git_branch": {
                                        "type": "string"
                                },
                                "user_request": {
                                        "type": "string"
                                },
                                "entity_name": {
                                        "type": "string"
                                },
                                "programming_language": {
                                        "type": "string",
                                        "enum": [
                                                "JAVA",
                                                "PYTHON"
                                        ]
                                }
                        },
                        "required": [
                                "user_request",
                                "git_branch",
                                "entity_name",
                                "programming_language"
                        ],
                        "additionalProperties": False
                }
        }
}
