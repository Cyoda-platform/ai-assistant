"""
InitSetupWorkflowJavaWorkflowConfig Configuration

Generated from config: workflow_configs/configs/init_setup_workflow_java.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.functions.not_stage_completed_85df.function import NotStageCompleted85dfFunctionConfig
from workflow_config_code.workflows.agents.configs.prompt_sent_956f.agent import PromptSent956fAgentConfig
from workflow_config_code.workflows.agents.configs.process_user_input_52da.agent import ProcessUserInput52daAgentConfig
from workflow_config_code.workflows.functions.is_stage_completed_ebb9.function import IsStageCompletedEbb9FunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_d5ca.function import IsStageCompletedD5caFunctionConfig
from workflow_config_code.workflows.functions.not_stage_completed_2f18.function import NotStageCompleted2f18FunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_cf58.function import IsStageCompletedCf58FunctionConfig
from workflow_config_code.workflows.functions.not_stage_completed_6d2b.function import NotStageCompleted6d2bFunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_e0d9.function import IsStageCompletedE0d9FunctionConfig
from workflow_config_code.workflows.agents.configs.prompt_sent_59d6.agent import PromptSent59d6AgentConfig
from workflow_config_code.workflows.functions.not_stage_completed_812b.function import NotStageCompleted812bFunctionConfig
from workflow_config_code.workflows.agents.configs.prompt_sent_68db.agent import PromptSent68dbAgentConfig
from workflow_config_code.workflows.agents.configs.process_user_input_f107.agent import ProcessUserInputF107AgentConfig
from workflow_config_code.workflows.agents.configs.process_user_input_e32d.agent import ProcessUserInputE32dAgentConfig
from workflow_config_code.workflows.agents.configs.process_user_input_dd02.agent import ProcessUserInputDd02AgentConfig
from workflow_config_code.workflows.agents.configs.prompt_sent_ef07.agent import PromptSentEf07AgentConfig
from workflow_config_code.workflows.functions.not_stage_completed_d1b6.function import NotStageCompletedD1b6FunctionConfig
from workflow_config_code.workflows.messages.lock_chat_1135.message import LockChat1135MessageConfig
from workflow_config_code.workflows.agents.configs.prompt_sent_a239.agent import PromptSentA239AgentConfig
from workflow_config_code.workflows.agents.configs.process_user_input_57d2.agent import ProcessUserInput57d2AgentConfig
from workflow_config_code.workflows.functions.is_stage_completed_68b2.function import IsStageCompleted68b2FunctionConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "init_setup_workflow_java",
        "desc": "Migrated from init_setup_workflow_java",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "init_setup_workflow_java",
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "start_chat",
                        "next": "app_requirements_requested",
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
            "app_requirements_requested": {
                "transitions": [
                    {
                        "name": "starting_chat",
                        "next": "prompt_app_requirements_step1",
                        "manual": False,
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_requested",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_requested",
                        "next": "locked_app_requirements_requested",
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
            "locked_app_requirements_requested": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_requested",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_requested",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_requested",
                        "next": "locked_locked_app_requirements_requested",
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
            "locked_locked_app_requirements_requested": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_requested",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_requested",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_requested",
                        "next": "locked_locked_locked_app_requirements_requested",
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
            "locked_locked_locked_app_requirements_requested": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_requested",
                        "manual": True,
                    },
                ],
            },
            "prompt_app_requirements_step1": {
                "transitions": [
                    {
                        "name": "prompt_sent",
                        "next": "app_requirements_step1",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.prompt_sent_59d6",
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
                        "next": "prompt_app_requirements_step1",
                        "manual": True,
                    },
                    {
                        "name": "fail_prompt_app_requirements_step1",
                        "next": "locked_prompt_app_requirements_step1",
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
            "locked_prompt_app_requirements_step1": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "prompt_app_requirements_step1",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_prompt_app_requirements_step1",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_prompt_app_requirements_step1",
                        "next": "locked_locked_prompt_app_requirements_step1",
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
            "locked_locked_prompt_app_requirements_step1": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_prompt_app_requirements_step1",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_prompt_app_requirements_step1",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_prompt_app_requirements_step1",
                        "next": "locked_locked_locked_prompt_app_requirements_step1",
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
            "locked_locked_locked_prompt_app_requirements_step1": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_prompt_app_requirements_step1",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step1": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_step1_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "manual_approve",
                        "next": "prompt_app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_step1_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_step1",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step1",
                        "next": "locked_app_requirements_step1",
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
            "locked_app_requirements_step1": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step1",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step1",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step1",
                        "next": "locked_locked_app_requirements_step1",
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
            "locked_locked_app_requirements_step1": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step1",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step1",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step1",
                        "next": "locked_locked_locked_app_requirements_step1",
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
            "locked_locked_locked_app_requirements_step1": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step1",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step1_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_step1_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_user_input_dd02",
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
                        "next": "app_requirements_step1_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step1_submitted_answer",
                        "next": "locked_app_requirements_step1_submitted_answer",
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
            "locked_app_requirements_step1_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step1_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step1_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step1_submitted_answer",
                        "next": "locked_locked_app_requirements_step1_submitted_answer",
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
            "locked_locked_app_requirements_step1_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step1_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step1_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step1_submitted_answer",
                        "next": "locked_locked_locked_app_requirements_step1_submitted_answer",
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
            "locked_locked_locked_app_requirements_step1_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step1_submitted_answer",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step1_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_1_processing",
                        "next": "app_requirements_step1",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.not_stage_completed_d1b6",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "process_app_setup_1_success",
                        "next": "prompt_app_requirements_step3",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_stage_completed_cf58",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_step1_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step1_processing",
                        "next": "locked_app_requirements_step1_processing",
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
            "locked_app_requirements_step1_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step1_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step1_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step1_processing",
                        "next": "locked_locked_app_requirements_step1_processing",
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
            "locked_locked_app_requirements_step1_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step1_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step1_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step1_processing",
                        "next": "locked_locked_locked_app_requirements_step1_processing",
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
            "locked_locked_locked_app_requirements_step1_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step1_processing",
                        "manual": True,
                    },
                ],
            },
            "prompt_app_requirements_step3": {
                "transitions": [
                    {
                        "name": "prompt_sent",
                        "next": "app_requirements_step3",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.prompt_sent_ef07",
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
                        "next": "prompt_app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "fail_prompt_app_requirements_step3",
                        "next": "locked_prompt_app_requirements_step3",
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
            "locked_prompt_app_requirements_step3": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "prompt_app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_prompt_app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_prompt_app_requirements_step3",
                        "next": "locked_locked_prompt_app_requirements_step3",
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
            "locked_locked_prompt_app_requirements_step3": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_prompt_app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_prompt_app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_prompt_app_requirements_step3",
                        "next": "locked_locked_locked_prompt_app_requirements_step3",
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
            "locked_locked_locked_prompt_app_requirements_step3": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_prompt_app_requirements_step3",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step3": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_step3_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "manual_approve",
                        "next": "prompt_app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_step3_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step3",
                        "next": "locked_app_requirements_step3",
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
            "locked_app_requirements_step3": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step3",
                        "next": "locked_locked_app_requirements_step3",
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
            "locked_locked_app_requirements_step3": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step3",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step3",
                        "next": "locked_locked_locked_app_requirements_step3",
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
            "locked_locked_locked_app_requirements_step3": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step3",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step3_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_step3_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_user_input_52da",
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
                        "next": "app_requirements_step3_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step3_submitted_answer",
                        "next": "locked_app_requirements_step3_submitted_answer",
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
            "locked_app_requirements_step3_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step3_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step3_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step3_submitted_answer",
                        "next": "locked_locked_app_requirements_step3_submitted_answer",
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
            "locked_locked_app_requirements_step3_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step3_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step3_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step3_submitted_answer",
                        "next": "locked_locked_locked_app_requirements_step3_submitted_answer",
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
            "locked_locked_locked_app_requirements_step3_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step3_submitted_answer",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step3_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_3_processing",
                        "next": "app_requirements_step3",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.not_stage_completed_2f18",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "process_app_setup_3_success",
                        "next": "prompt_app_requirements_step4",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_stage_completed_d5ca",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_step3_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step3_processing",
                        "next": "locked_app_requirements_step3_processing",
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
            "locked_app_requirements_step3_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step3_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step3_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step3_processing",
                        "next": "locked_locked_app_requirements_step3_processing",
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
            "locked_locked_app_requirements_step3_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step3_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step3_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step3_processing",
                        "next": "locked_locked_locked_app_requirements_step3_processing",
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
            "locked_locked_locked_app_requirements_step3_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step3_processing",
                        "manual": True,
                    },
                ],
            },
            "prompt_app_requirements_step4": {
                "transitions": [
                    {
                        "name": "prompt_sent",
                        "next": "app_requirements_step4",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.prompt_sent_a239",
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
                        "next": "prompt_app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "fail_prompt_app_requirements_step4",
                        "next": "locked_prompt_app_requirements_step4",
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
            "locked_prompt_app_requirements_step4": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "prompt_app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_prompt_app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_prompt_app_requirements_step4",
                        "next": "locked_locked_prompt_app_requirements_step4",
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
            "locked_locked_prompt_app_requirements_step4": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_prompt_app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_prompt_app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_prompt_app_requirements_step4",
                        "next": "locked_locked_locked_prompt_app_requirements_step4",
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
            "locked_locked_locked_prompt_app_requirements_step4": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_prompt_app_requirements_step4",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step4": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_step4_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "manual_approve",
                        "next": "prompt_app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_step4_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step4",
                        "next": "locked_app_requirements_step4",
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
            "locked_app_requirements_step4": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step4",
                        "next": "locked_locked_app_requirements_step4",
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
            "locked_locked_app_requirements_step4": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step4",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step4",
                        "next": "locked_locked_locked_app_requirements_step4",
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
            "locked_locked_locked_app_requirements_step4": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step4",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step4_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_step4_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_user_input_57d2",
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
                        "next": "app_requirements_step4_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step4_submitted_answer",
                        "next": "locked_app_requirements_step4_submitted_answer",
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
            "locked_app_requirements_step4_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step4_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step4_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step4_submitted_answer",
                        "next": "locked_locked_app_requirements_step4_submitted_answer",
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
            "locked_locked_app_requirements_step4_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step4_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step4_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step4_submitted_answer",
                        "next": "locked_locked_locked_app_requirements_step4_submitted_answer",
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
            "locked_locked_locked_app_requirements_step4_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step4_submitted_answer",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step4_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_4_processing",
                        "next": "app_requirements_step4",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.not_stage_completed_6d2b",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "process_app_setup_4_success",
                        "next": "prompt_app_requirements_step5",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_stage_completed_ebb9",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_step4_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step4_processing",
                        "next": "locked_app_requirements_step4_processing",
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
            "locked_app_requirements_step4_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step4_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step4_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step4_processing",
                        "next": "locked_locked_app_requirements_step4_processing",
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
            "locked_locked_app_requirements_step4_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step4_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step4_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step4_processing",
                        "next": "locked_locked_locked_app_requirements_step4_processing",
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
            "locked_locked_locked_app_requirements_step4_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step4_processing",
                        "manual": True,
                    },
                ],
            },
            "prompt_app_requirements_step5": {
                "transitions": [
                    {
                        "name": "prompt_sent",
                        "next": "app_requirements_step5",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.prompt_sent_68db",
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
                        "next": "prompt_app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "fail_prompt_app_requirements_step5",
                        "next": "locked_prompt_app_requirements_step5",
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
            "locked_prompt_app_requirements_step5": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "prompt_app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_prompt_app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_prompt_app_requirements_step5",
                        "next": "locked_locked_prompt_app_requirements_step5",
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
            "locked_locked_prompt_app_requirements_step5": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_prompt_app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_prompt_app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_prompt_app_requirements_step5",
                        "next": "locked_locked_locked_prompt_app_requirements_step5",
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
            "locked_locked_locked_prompt_app_requirements_step5": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_prompt_app_requirements_step5",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step5": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_step5_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "manual_approve",
                        "next": "prompt_app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_step5_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step5",
                        "next": "locked_app_requirements_step5",
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
            "locked_app_requirements_step5": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step5",
                        "next": "locked_locked_app_requirements_step5",
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
            "locked_locked_app_requirements_step5": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step5",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step5",
                        "next": "locked_locked_locked_app_requirements_step5",
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
            "locked_locked_locked_app_requirements_step5": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step5",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step5_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_step5_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_user_input_e32d",
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
                        "next": "app_requirements_step5_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step5_submitted_answer",
                        "next": "locked_app_requirements_step5_submitted_answer",
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
            "locked_app_requirements_step5_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step5_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step5_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step5_submitted_answer",
                        "next": "locked_locked_app_requirements_step5_submitted_answer",
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
            "locked_locked_app_requirements_step5_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step5_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step5_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step5_submitted_answer",
                        "next": "locked_locked_locked_app_requirements_step5_submitted_answer",
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
            "locked_locked_locked_app_requirements_step5_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step5_submitted_answer",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step5_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_5_processing",
                        "next": "app_requirements_step5",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.not_stage_completed_812b",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "process_app_setup_5_success",
                        "next": "prompt_app_requirements_step6",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_stage_completed_68b2",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_step5_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step5_processing",
                        "next": "locked_app_requirements_step5_processing",
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
            "locked_app_requirements_step5_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step5_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step5_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step5_processing",
                        "next": "locked_locked_app_requirements_step5_processing",
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
            "locked_locked_app_requirements_step5_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step5_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step5_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step5_processing",
                        "next": "locked_locked_locked_app_requirements_step5_processing",
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
            "locked_locked_locked_app_requirements_step5_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step5_processing",
                        "manual": True,
                    },
                ],
            },
            "prompt_app_requirements_step6": {
                "transitions": [
                    {
                        "name": "prompt_sent",
                        "next": "app_requirements_step6",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.prompt_sent_956f",
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
                        "next": "prompt_app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "fail_prompt_app_requirements_step6",
                        "next": "locked_prompt_app_requirements_step6",
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
            "locked_prompt_app_requirements_step6": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "prompt_app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_prompt_app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_prompt_app_requirements_step6",
                        "next": "locked_locked_prompt_app_requirements_step6",
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
            "locked_locked_prompt_app_requirements_step6": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_prompt_app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_prompt_app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_prompt_app_requirements_step6",
                        "next": "locked_locked_locked_prompt_app_requirements_step6",
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
            "locked_locked_locked_prompt_app_requirements_step6": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_prompt_app_requirements_step6",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step6": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_step6_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "manual_approve",
                        "next": "ready_to_lock_chat",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_step6_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step6",
                        "next": "locked_app_requirements_step6",
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
            "locked_app_requirements_step6": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step6",
                        "next": "locked_locked_app_requirements_step6",
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
            "locked_locked_app_requirements_step6": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step6",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step6",
                        "next": "locked_locked_locked_app_requirements_step6",
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
            "locked_locked_locked_app_requirements_step6": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step6",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step6_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_step6_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_user_input_f107",
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
                        "next": "app_requirements_step6_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step6_submitted_answer",
                        "next": "locked_app_requirements_step6_submitted_answer",
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
            "locked_app_requirements_step6_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step6_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step6_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step6_submitted_answer",
                        "next": "locked_locked_app_requirements_step6_submitted_answer",
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
            "locked_locked_app_requirements_step6_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step6_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step6_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step6_submitted_answer",
                        "next": "locked_locked_locked_app_requirements_step6_submitted_answer",
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
            "locked_locked_locked_app_requirements_step6_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step6_submitted_answer",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_step6_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_6_processing",
                        "next": "app_requirements_step6",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.not_stage_completed_85df",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "process_app_setup_6_success",
                        "next": "ready_to_lock_chat",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_stage_completed_e0d9",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_step6_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_step6_processing",
                        "next": "locked_app_requirements_step6_processing",
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
            "locked_app_requirements_step6_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_step6_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_step6_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_step6_processing",
                        "next": "locked_locked_app_requirements_step6_processing",
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
            "locked_locked_app_requirements_step6_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_step6_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_app_requirements_step6_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_app_requirements_step6_processing",
                        "next": "locked_locked_locked_app_requirements_step6_processing",
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
            "locked_locked_locked_app_requirements_step6_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_app_requirements_step6_processing",
                        "manual": True,
                    },
                ],
            },
            "ready_to_lock_chat": {
                "transitions": [
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.lock_chat_1135",
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
                        "next": "ready_to_lock_chat",
                        "manual": True,
                    },
                    {
                        "name": "fail_ready_to_lock_chat",
                        "next": "locked_ready_to_lock_chat",
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
            "locked_ready_to_lock_chat": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "ready_to_lock_chat",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_ready_to_lock_chat",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_ready_to_lock_chat",
                        "next": "locked_locked_ready_to_lock_chat",
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
            "locked_locked_ready_to_lock_chat": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_ready_to_lock_chat",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_ready_to_lock_chat",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_ready_to_lock_chat",
                        "next": "locked_locked_locked_ready_to_lock_chat",
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
            "locked_locked_locked_ready_to_lock_chat": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_ready_to_lock_chat",
                        "manual": True,
                    },
                ],
            },
        },
    }
