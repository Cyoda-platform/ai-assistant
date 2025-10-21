"""
ChatEntityWorkflowConfig Configuration

Generated from config: workflow_configs/configs/chat_entity.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.functions.is_chat_unlocked_f77c.function import IsChatUnlockedF77cFunctionConfig
from workflow_config_code.workflows.functions.is_chat_locked_5b22.function import IsChatLocked5b22FunctionConfig
from workflow_config_code.workflows.agents.configs.submit_answer_4a45.agent import SubmitAnswer4a45AgentConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "chat_entity",
        "desc": "Migrated from chat_entity",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "chat_entity",
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
            "initialized_chat": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "submitted_workflow_question",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.submit_answer_4a45",
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
            "submitted_workflow_question": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "processed_question",
                        "manual": True,
                        "processors": [
                            {
                                "name": "AgentProcessor.submit_answer_4a45",
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        ],
                    },
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_chat_locked_5b22",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "retry",
                        "next": "submitted_workflow_question",
                        "manual": True,
                    },
                    {
                        "name": "fail_submitted_workflow_question",
                        "next": "locked_submitted_workflow_question",
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
            "locked_submitted_workflow_question": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "submitted_workflow_question",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_submitted_workflow_question",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_submitted_workflow_question",
                        "next": "locked_locked_submitted_workflow_question",
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
            "processed_question": {
                "transitions": [
                    {
                        "name": "rollback",
                        "next": "locked_chat",
                        "manual": True,
                    },
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_chat_locked_5b22",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "unlock_chat",
                        "next": "submitted_workflow_question",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_chat_unlocked_f77c",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "retry",
                        "next": "processed_question",
                        "manual": True,
                    },
                    {
                        "name": "fail_processed_question",
                        "next": "locked_processed_question",
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
            "locked_processed_question": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "processed_question",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_processed_question",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_processed_question",
                        "next": "locked_locked_processed_question",
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
            "locked_chat": {
                "transitions": [
                    {
                        "name": "unlock_chat",
                        "next": "submitted_workflow_question",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_chat",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_chat",
                        "next": "locked_locked_chat",
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
        },
    }
