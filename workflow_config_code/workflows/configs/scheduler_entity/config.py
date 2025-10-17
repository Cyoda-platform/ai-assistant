"""
SchedulerEntityWorkflowConfig Configuration

Generated from config: workflow_configs/configs/scheduler_entity.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.functions.check_scheduled_entity_status_4d37.function import CheckScheduledEntityStatus4d37FunctionConfig
from workflow_config_code.workflows.functions.trigger_parent_entity_b4c4.function import TriggerParentEntityB4c4FunctionConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "scheduler_entity",
        "desc": "Scheduler entity workflow for managing scheduled processes",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "scheduler_entity",
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "schedule",
                        "next": "scheduled",
                        "manual": False,
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
                ],
            },
            "scheduled": {
                "transitions": [
                    {
                        "name": "wait",
                        "next": "waiting",
                        "manual": False,
                        "processors": [
                            {
                                "type": "scheduled",
                                "name": "schedule_close_process",
                                "config": {
                                    "delayMs": 30000,
                                    "timeoutMs": 3600000,
                                    "transition": "check_status",
                                },
                            },
                        ],
                    },
                    {
                        "name": "retry",
                        "next": "scheduled",
                        "manual": True,
                    },
                    {
                        "name": "fail_scheduled",
                        "next": "locked_scheduled",
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
            "locked_scheduled": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "scheduled",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_scheduled",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_scheduled",
                        "next": "locked_locked_scheduled",
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
            "locked_locked_scheduled": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_scheduled",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_scheduled",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_scheduled",
                        "next": "locked_locked_locked_scheduled",
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
            "locked_locked_locked_scheduled": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_scheduled",
                        "manual": True,
                    },
                ],
            },
            "waiting": {
                "transitions": [
                    {
                        "name": "check_status",
                        "next": "checked_status",
                        "manual": True,
                        "processors": [
                            {
                                "name": "FunctionProcessor.check_scheduled_entity_status_4d37",
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
                        "next": "waiting",
                        "manual": True,
                    },
                    {
                        "name": "fail_waiting",
                        "next": "locked_waiting",
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
            "locked_waiting": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "waiting",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_waiting",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_waiting",
                        "next": "locked_locked_waiting",
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
            "locked_locked_waiting": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_waiting",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_waiting",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_waiting",
                        "next": "locked_locked_locked_waiting",
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
            "locked_locked_locked_waiting": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_waiting",
                        "manual": True,
                    },
                ],
            },
            "checked_status": {
                "transitions": [
                    {
                        "name": "complete",
                        "next": "complete",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.status",
                                    "operation": "IEQUALS",
                                    "value": "complete",
                                },
                            ],
                        },
                    },
                    {
                        "name": "wait",
                        "next": "scheduled",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.status",
                                    "operation": "IEQUALS",
                                    "value": "in_progress",
                                },
                            ],
                        },
                    },
                    {
                        "name": "error",
                        "next": "error",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.status",
                                    "operation": "IEQUALS",
                                    "value": "error",
                                },
                            ],
                        },
                    },
                    {
                        "name": "retry",
                        "next": "checked_status",
                        "manual": True,
                    },
                    {
                        "name": "fail_checked_status",
                        "next": "locked_checked_status",
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
            "locked_checked_status": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "checked_status",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_checked_status",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_checked_status",
                        "next": "locked_locked_checked_status",
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
            "locked_locked_checked_status": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_checked_status",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_checked_status",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_checked_status",
                        "next": "locked_locked_locked_checked_status",
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
            "locked_locked_locked_checked_status": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_checked_status",
                        "manual": True,
                    },
                ],
            },
            "complete": {
                "transitions": [
                    {
                        "name": "trigger_parent_entity",
                        "next": "unlocked_parent_entity",
                        "manual": False,
                        "processors": [
                            {
                                "name": "FunctionProcessor.trigger_parent_entity_b4c4",
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
                        "next": "complete",
                        "manual": True,
                    },
                    {
                        "name": "fail_complete",
                        "next": "locked_complete",
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
            "locked_complete": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "complete",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_complete",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_complete",
                        "next": "locked_locked_complete",
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
            "locked_locked_complete": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_complete",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_complete",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_complete",
                        "next": "locked_locked_locked_complete",
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
            "locked_locked_locked_complete": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_complete",
                        "manual": True,
                    },
                ],
            },
            "unlocked_parent_entity": {
                "transitions": [
                    {
                        "name": "finish",
                        "next": "finished",
                        "manual": False,
                    },
                    {
                        "name": "retry",
                        "next": "unlocked_parent_entity",
                        "manual": True,
                    },
                    {
                        "name": "fail_unlocked_parent_entity",
                        "next": "locked_unlocked_parent_entity",
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
            "locked_unlocked_parent_entity": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "unlocked_parent_entity",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_unlocked_parent_entity",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_unlocked_parent_entity",
                        "next": "locked_locked_unlocked_parent_entity",
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
            "locked_locked_unlocked_parent_entity": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_unlocked_parent_entity",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_unlocked_parent_entity",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_unlocked_parent_entity",
                        "next": "locked_locked_locked_unlocked_parent_entity",
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
            "locked_locked_locked_unlocked_parent_entity": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_unlocked_parent_entity",
                        "manual": True,
                    },
                ],
            },
            "error": {
                "transitions": [
                    {
                        "name": "retry",
                        "next": "error",
                        "manual": True,
                    },
                    {
                        "name": "fail_error",
                        "next": "locked_error",
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
            "locked_error": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "error",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_error",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_error",
                        "next": "locked_locked_error",
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
            "locked_locked_error": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_error",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_error",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_error",
                        "next": "locked_locked_locked_error",
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
            "locked_locked_locked_error": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_error",
                        "manual": True,
                    },
                ],
            },
            "finished": {
                "transitions": [
                    {
                        "name": "retry",
                        "next": "finished",
                        "manual": True,
                    },
                    {
                        "name": "fail_finished",
                        "next": "locked_finished",
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
            "locked_finished": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "finished",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_finished",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_finished",
                        "next": "locked_locked_finished",
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
            "locked_locked_finished": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_finished",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_finished",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_finished",
                        "next": "locked_locked_locked_finished",
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
            "locked_locked_locked_finished": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_finished",
                        "manual": True,
                    },
                ],
            },
        },
    }
