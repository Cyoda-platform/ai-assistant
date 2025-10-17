"""
EditGeneralApplicationPythonWorkflowConfig Configuration

Generated from config: workflow_configs/configs/edit_general_application_python.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.messages.notify_editing_started.message import NotifyEditingStartedMessageConfig
from workflow_config_code.workflows.agents.configs.process_user_input_57d2_py.agent import ProcessUserInput57d2PyAgentConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "edit_general_application_python",
        "desc": "Complete workflow to transform functional requirements into a working application",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "edit_general_application_python",
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "start_edit_application",
                        "next": "edit_application_requested",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.notify_editing_started",
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        ],
                    },
                    {
                        "name": "retry",
                        "next": "initial_state",
                        "manual": True,
                    },
                    {
                        "name": "fail_initial_state",
                        "next": "locked_initial_state",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_initial_state": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "initial_state",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_initial_state",
                        "next": "locked_locked_initial_state",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_initial_state": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_initial_state",
                        "next": "locked_locked_locked_initial_state",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_initial_state": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_initial_state",
                        "next": "locked_locked_locked_locked_initial_state",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_initial_state": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_locked_initial_state",
                        "next": "locked_locked_locked_locked_locked_initial_state",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_locked_initial_state": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_locked_initial_state",
                        "manual": True,
                    },
                ],
            },
            "processing_user_input": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "manual_approve",
                        "next": "edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "processing_user_input",
                        "manual": True,
                    },
                    {
                        "name": "fail_processing_user_input",
                        "next": "locked_processing_user_input",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_processing_user_input": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "processing_user_input",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_processing_user_input",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_processing_user_input",
                        "next": "locked_locked_processing_user_input",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_processing_user_input": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_processing_user_input",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_processing_user_input",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_processing_user_input",
                        "next": "locked_locked_locked_processing_user_input",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_processing_user_input": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_processing_user_input",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_processing_user_input",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_processing_user_input",
                        "next": "locked_locked_locked_locked_processing_user_input",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_processing_user_input": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_processing_user_input",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_locked_processing_user_input",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_locked_processing_user_input",
                        "next": "locked_locked_locked_locked_locked_processing_user_input",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_locked_processing_user_input": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_locked_processing_user_input",
                        "manual": True,
                    },
                ],
            },
            "edit_application_requested": {
                "transitions": [
                    {
                        "name": "edit_application_requested_processing",
                        "next": "processing_user_input",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_user_input_57d2_py",
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000,
                                },
                            },
                        ],
                    },
                    {
                        "name": "retry",
                        "next": "edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "fail_edit_application_requested",
                        "next": "locked_edit_application_requested",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_edit_application_requested": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_edit_application_requested",
                        "next": "locked_locked_edit_application_requested",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_edit_application_requested": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_edit_application_requested",
                        "next": "locked_locked_locked_edit_application_requested",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_edit_application_requested": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_edit_application_requested",
                        "next": "locked_locked_locked_locked_edit_application_requested",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_edit_application_requested": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_locked_edit_application_requested",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_locked_edit_application_requested",
                        "next": "locked_locked_locked_locked_locked_edit_application_requested",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_locked_edit_application_requested": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_locked_edit_application_requested",
                        "manual": True,
                    },
                ],
            },
        },
    }
