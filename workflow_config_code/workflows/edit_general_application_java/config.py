"""
FunctionalRequirementsToPrototypeJavaWorkflowConfig Configuration

Configuration data for the functional requirements to application workflow.
"""

from typing import Any, Dict, Callable

from workflow_config_code.agents.process_user_input_2185.agent import ProcessUserInput2185AgentConfig
from workflow_config_code.tools.is_stage_completed_c00a.tool import IsStageCompletedC00aToolConfig
from workflow_config_code.tools.not_stage_completed_6044.tool import NotStageCompleted6044ToolConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "Functional Requirements to Prototype Workflow",
        "desc": "Complete workflow to transform functional requirements into a working application",
        "initialState": "initial_state",
        "active": True,
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "start_edit_application",
                        "next": "edit_application_requested",
                        "manual": False
                    }
                ]
            },
            "process_user_input": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "edit_application_requested",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "edit_application_requested",
                        "manual": True
                    }
                ]
            },
            "edit_application_requested": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "edit_application_requested_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessUserInput2185AgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "edit_application_requested_processing": {
                "transitions": [
                    {
                        "name": "edit_application_requested_processing",
                        "next": "process_user_input",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": NotStageCompleted6044ToolConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    },
                    {
                        "name": "process_migration_confirmation_success",
                        "next": "lock_chat",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsStageCompletedC00aToolConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    }
                ]
            },
            "lock_chat": {
                "transitions": [
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False
                    }
                ]
            }
        }
    }
