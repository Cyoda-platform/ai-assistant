"""
EditExistingAppDesignAdditionalFeatureE0e4ToolConfig Configuration

Generated from config: workflow_configs/tools/edit_existing_app_design_additional_feature_e0e4/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "edit_existing_app_design_additional_feature",
                "description": "Launches workflow that is necessary to help the user plan how to edit an existing application or add a new feature. Key factor is that an application already exists. if the user doesn't specify the branch, ask yourself.",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "git_branch": {
                                        "type": "string"
                                },
                                "user_request": {
                                        "type": "string"
                                }
                        },
                        "required": [
                                "user_request",
                                "git_branch"
                        ],
                        "additionalProperties": False
                }
        }
}
