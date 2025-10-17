"""
ChatBusinessEntityWorkflowConfig Configuration

Generated from config: workflow_configs/configs/chat_business_entity.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable



def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "chat_business_entity",
        "desc": "Migrated from chat_business_entity",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "chat_business_entity",
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "initialize_chat",
                        "next": "initialized_chat",
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
            "initialized_chat": {
                "transitions": [
                    {
                        "name": "update_transition",
                        "next": "initialized_chat",
                        "manual": True,
                    },
                    {
                        "name": "delete",
                        "next": "deleted",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "initialized_chat",
                        "manual": True,
                    },
                    {
                        "name": "fail_initialized_chat",
                        "next": "locked_initialized_chat",
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
            "locked_initialized_chat": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "initialized_chat",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_initialized_chat",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_initialized_chat",
                        "next": "locked_locked_initialized_chat",
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
            "locked_locked_initialized_chat": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_initialized_chat",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_initialized_chat",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_initialized_chat",
                        "next": "locked_locked_locked_initialized_chat",
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
            "locked_locked_locked_initialized_chat": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_initialized_chat",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_initialized_chat",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_initialized_chat",
                        "next": "locked_locked_locked_locked_initialized_chat",
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
            "locked_locked_locked_locked_initialized_chat": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_initialized_chat",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_locked_initialized_chat",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_locked_initialized_chat",
                        "next": "locked_locked_locked_locked_locked_initialized_chat",
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
            "locked_locked_locked_locked_locked_initialized_chat": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_locked_initialized_chat",
                        "manual": True,
                    },
                ],
            },
        },
    }
