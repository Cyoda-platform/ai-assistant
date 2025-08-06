"""
ResumeBuildGeneralApplication2af7ToolConfig Configuration

Generated from config: workflow_configs/tools/resume_build_general_application_2af7/tool.json
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {
        "type": "function",
        "function": {
                "name": "resume_build_general_application",
                "description": "Resumes building an application by branch_name. Use for queries like, please proceed with this app; i had an error - proceed building an app, continue/resume this app/chat. Please ask to specify a programming language. Transition, git branch and programming language should be provided by the user! You cannot decide yourself. The user doesn't know what the transitions mean so you might want to ask: have you finished the functional requirements (if no - discuss_functional_requirements or edit_functional_requirements), then - have they succeeded with the app prototype (if no: prototype_discussion_requested), have they confirmed the start of migration (if no: resume_migration)? Did they have issues after the start of migration (yes - resume_migration) , do they need setup assistance (resume_post_app_build_steps)?",
                "strict": True,
                "parameters": {
                        "type": "object",
                        "properties": {
                                "user_request": {
                                        "type": "string"
                                },
                                "programming_language": {
                                        "type": "string",
                                        "enum": [
                                                "JAVA",
                                                "PYTHON"
                                        ]
                                },
                                "git_branch": {
                                        "type": "string"
                                },
                                "transition": {
                                        "type": "string",
                                        "enum": [
                                                "build_new_app",
                                                "discuss_functional_requirements",
                                                "edit_functional_requirements",
                                                "prototype_discussion_requested",
                                                "resume_migration",
                                                "resume_prototype_cyoda_workflow",
                                                "resume_gen_prototype_cyoda_workflow_json",
                                                "resume_gen_entities",
                                                "resume_post_app_build_steps"
                                        ]
                                }
                        },
                        "required": [
                                "user_request",
                                "git_branch",
                                "transition",
                                "programming_language"
                        ],
                        "additionalProperties": False
                }
        }
}
