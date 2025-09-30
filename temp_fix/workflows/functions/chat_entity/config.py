"""
ChatEntityWorkflowConfig Configuration

Generated from config: workflow_configs/workflows/chat_entity.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.submit_answer_4a45.agent import SubmitAnswer4a45AgentConfig
from workflow_config_code.workflows.agents.submit_answer_b135.agent import SubmitAnswerB135AgentConfig
from workflow_config_code.workflows.functions.is_chat_locked_5b22.function import IsChatLocked5b22FunctionConfig
from workflow_config_code.workflows.functions.is_chat_unlocked_f77c.function import IsChatUnlockedF77cFunctionConfig


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
            "value": "chat_entity"
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "initialize_chat",
                        "next": "initialized_chat",
                        "manual": False
                    }
                ]
            },
            "initialized_chat": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "submitted_workflow_question",
                        "manual": False,
                        "processors": [
                            {
                                "name": SubmitAnswer4a45AgentConfig.get_name(),
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
            "submitted_workflow_question": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "processed_question",
                        "manual": True,
                        "processors": [
                            {
                                "name": SubmitAnswer4a45AgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    },
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsChatLocked5b22FunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    }
                ]
            },
            "processed_question": {
                "transitions": [
                    {
                        "name": "rollback",
                        "next": "locked_chat",
                        "manual": True
                    },
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsChatLocked5b22FunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    },
                    {
                        "name": "unlock_chat",
                        "next": "submitted_workflow_question",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsChatUnlockedF77cFunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    }
                ]
            },
            "locked_chat": {
                "transitions": [
                    {
                        "name": "unlock_chat",
                        "next": "submitted_workflow_question",
                        "manual": True
                    }
                ]
            }
        }
    }
