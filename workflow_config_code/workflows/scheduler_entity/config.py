"""
SchedulerEntityWorkflowConfig Configuration

Generated from config: workflow_configs/workflows/scheduler_entity.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.check_scheduled_entity_status_4d37.tool import CheckScheduledEntityStatus4d37ToolConfig
from workflow_config_code.tools.trigger_parent_entity_b4c4.tool import TriggerParentEntityB4c4ToolConfig
from workflow_config_code.tools.schedule_close_process_b2b5.tool import ScheduleCloseProcessB2b5ToolConfig


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
            "value": "scheduler_entity"
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "schedule",
                        "next": "scheduled",
                        "manual": False
                    }
                ]
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
                                    "transition": "check_status"
                                }
                            }
                        ]
                    }
                ]
            },
            "waiting": {
                "transitions": [
                    {
                        "name": "check_status",
                        "next": "checked_status",
                        "manual": True,
                        "processors": [
                            {
                                "name": CheckScheduledEntityStatus4d37ToolConfig.get_name(),
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
                                    "value": "complete"
                                }
                            ]
                        }
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
                                    "value": "in_progress"
                                }
                            ]
                        }
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
                                    "value": "error"
                                }
                            ]
                        }
                    }
                ]
            },
            "complete": {
                "transitions": [
                    {
                        "name": "trigger_parent_entity",
                        "next": "unlocked_parent_entity",
                        "manual": False,
                        "processors": [
                            {
                                "name": TriggerParentEntityB4c4ToolConfig.get_name(),
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
            "unlocked_parent_entity": {
                "transitions": [
                    {
                        "name": "finish",
                        "next": "finished",
                        "manual": False
                    }
                ]
            },
            "error": {
                "transitions": []
            },
            "finished": {
                "transitions": []
            }
        }
    }
