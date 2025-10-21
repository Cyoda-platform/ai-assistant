"""
EditGeneralApplicationPythonWorkflowConfig Configuration

Workflow for editing existing Python applications.
Similar to build workflow but uses user-defined repository URL without creating new branches.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.configs.process_user_input_9a8e.agent import ProcessUserInput9a8eAgentConfig
from workflow_config_code.workflows.agents.configs.edit_app_python.agent import EditAppPythonAgentConfig
from workflow_config_code.workflows.functions.init_setup_workflow_5f06.function import InitSetupWorkflow5f06FunctionConfig
from workflow_config_code.workflows.functions.save_env_file_d2aa.function import SaveEnvFileD2aaFunctionConfig
from workflow_config_code.workflows.functions.not_stage_completed_f259.function import NotStageCompletedF259FunctionConfig
from workflow_config_code.workflows.messages.notify_editing_requirements_discussion_python.message import NotifyEditingRequirementsDiscussionPythonMessageConfig
from workflow_config_code.workflows.agents.configs.process_user_input_2c31_optimized.agent import ProcessUserInput2c31OptimizedAgentConfig
from workflow_config_code.workflows.functions.is_stage_completed_b809.function import IsStageCompletedB809FunctionConfig
from workflow_config_code.workflows.functions.delete_files_6818.function import DeleteFiles6818FunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_e7bf.function import IsStageCompletedE7bfFunctionConfig
from workflow_config_code.workflows.functions.init_chats_for_editing_e8f3.function import InitChatsForEditingE8f3FunctionConfig
from workflow_config_code.workflows.messages.notify_started_application_generation.message import NotifyStartedApplicationGenerationMessageConfig
from workflow_config_code.workflows.agents.configs.notify_user_env_deployed_58e2.agent import NotifyUserEnvDeployed58e2AgentConfig
from workflow_config_code.workflows.messages.notify_editing_complete.message import NotifyEditingCompleteMessageConfig
from workflow_config_code.workflows.messages.notify_editing_started.message import NotifyEditingStartedMessageConfig
from workflow_config_code.workflows.functions.not_stage_completed_f57d.function import NotStageCompletedF57dFunctionConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "edit_general_application_python",
        "desc": "Complete workflow to edit existing Python applications using user-defined repository",
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
                        "name": "initialize",
                        "next": "initialized",
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
            "initialized": {
                "transitions": [
                    {
                        "name": "start_editing",
                        "next": "editing_started",
                        "manual": False,
                    },
                    {
                        "name": "retry",
                        "next": "initialized",
                        "manual": True,
                    },
                    {
                        "name": "fail_initialized",
                        "next": "locked_initialized",
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
            "locked_initialized": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "initialized",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_initialized",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_initialized",
                        "next": "locked_initialized",
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
            "editing_started": {
                "transitions": [
                    {
                        "name": "notify_editing",
                        "next": "repository_ready",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.notify_editing_started",
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
                        "next": "editing_started",
                        "manual": True,
                    },
                    {
                        "name": "fail_editing_started",
                        "next": "locked_editing_started",
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
            "locked_editing_started": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "editing_started",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_editing_started",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_editing_started",
                        "next": "locked_editing_started",
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
            "repository_ready": {
                "transitions": [
                    {
                        "name": "notify_editing_requirements_discussion_python",
                        "next": "app_requirements_requested",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.notify_editing_requirements_discussion_python",
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
                        "next": "repository_ready",
                        "manual": True,
                    },
                    {
                        "name": "fail_repository_ready",
                        "next": "locked_repository_ready",
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
            "locked_repository_ready": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "repository_ready",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_repository_ready",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_repository_ready",
                        "next": "locked_repository_ready",
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
            "app_requirements_requested": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "app_requirements_requested_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "manual_approve",
                        "next": "app_requirements_finalized",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "app_requirements_requested_submitted_answer",
                        "manual": True,
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
            "app_requirements_requested_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "app_requirements_requested_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_user_input_2c31_optimized",
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
                        "next": "app_requirements_requested_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_requested_submitted_answer",
                        "next": "locked_app_requirements_requested_submitted_answer",
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
            "locked_app_requirements_requested_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_requested_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_requested_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_requested_submitted_answer",
                        "next": "locked_app_requirements_requested_submitted_answer",
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
            "app_requirements_requested_processing": {
                "transitions": [
                    {
                        "name": "process_application_requirement_processing",
                        "next": "app_requirements_requested",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.not_stage_completed_f57d",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "process_application_requirement_success",
                        "next": "app_requirements_finalized",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_stage_completed_e7bf",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        },
                    },
                    {
                        "name": "retry",
                        "next": "app_requirements_requested_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_requested_processing",
                        "next": "locked_app_requirements_requested_processing",
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
            "locked_app_requirements_requested_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_requested_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_requested_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_requested_processing",
                        "next": "locked_app_requirements_requested_processing",
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
            "app_requirements_finalized": {
                "transitions": [
                    {
                        "name": "ask_about_api",
                        "next": "proceed_to_saving_files",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.notify_started_application_generation",
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
                        "next": "app_requirements_finalized",
                        "manual": True,
                    },
                    {
                        "name": "fail_app_requirements_finalized",
                        "next": "locked_app_requirements_finalized",
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
            "locked_app_requirements_finalized": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "app_requirements_finalized",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_app_requirements_finalized",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_app_requirements_finalized",
                        "next": "locked_app_requirements_finalized",
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
            "proceed_to_saving_files": {
                "transitions": [
                    {
                        "name": "init_chats_for_editing",
                        "next": "env_deployment_notified",
                        "manual": False,
                        "processors": [
                            {
                                "name": "FunctionProcessor.init_chats_for_editing_e8f3",
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
                        "next": "proceed_to_saving_files",
                        "manual": True,
                    },
                    {
                        "name": "fail_proceed_to_saving_files",
                        "next": "locked_proceed_to_saving_files",
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
            "locked_proceed_to_saving_files": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "proceed_to_saving_files",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_proceed_to_saving_files",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_proceed_to_saving_files",
                        "next": "locked_proceed_to_saving_files",
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
            "env_deployment_notified": {
                "transitions": [
                    {
                        "name": "process_user_input_1",
                        "next": "app_requirements_step3_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_user_input_9a8e",
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
                        "next": "env_deployment_notified",
                        "manual": True,
                    },
                    {
                        "name": "fail_env_deployment_notified",
                        "next": "locked_env_deployment_notified",
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
            "locked_env_deployment_notified": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "env_deployment_notified",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_env_deployment_notified",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_env_deployment_notified",
                        "next": "locked_env_deployment_notified",
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
            "app_requirements_step3_processing": {
                "transitions": [
                    {
                        "name": "process_app_setup_3_processing",
                        "next": "waiting_for_user_deployment_input",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.not_stage_completed_f259",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000,
                                },
                            },
                        },
                    },
                    {
                        "name": "process_app_setup_3_success",
                        "next": "deployed_cyoda_env",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_stage_completed_b809",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000,
                                },
                            },
                        },
                    },
                    {
                        "name": "rollback",
                        "next": "deployed_cyoda_env",
                        "manual": True,
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
            "waiting_for_user_deployment_input": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "env_deployment_notified",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "env_deployment_notified",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "waiting_for_user_deployment_input",
                        "manual": True,
                    },
                    {
                        "name": "fail_waiting_for_user_deployment_input",
                        "next": "locked_waiting_for_user_deployment_input",
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
            "locked_waiting_for_user_deployment_input": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "waiting_for_user_deployment_input",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_waiting_for_user_deployment_input",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_waiting_for_user_deployment_input",
                        "next": "locked_waiting_for_user_deployment_input",
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
            "deployed_cyoda_env": {
                "transitions": [
                    {
                        "name": "notify_user_env_deployed",
                        "next": "prototype_generation_started",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.notify_user_env_deployed_58e2",
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
                        "next": "deployed_cyoda_env",
                        "manual": True,
                    },
                    {
                        "name": "fail_deployed_cyoda_env",
                        "next": "locked_deployed_cyoda_env",
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
            "locked_deployed_cyoda_env": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "deployed_cyoda_env",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_deployed_cyoda_env",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_deployed_cyoda_env",
                        "next": "locked_deployed_cyoda_env",
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
            "prototype_generation_started": {
                "transitions": [
                    {
                        "name": "start_editing_application",
                        "next": "waiting_for_app_build",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.edit_app_python",
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
                        "next": "prototype_generation_started",
                        "manual": True,
                    },
                    {
                        "name": "fail_prototype_generation_started",
                        "next": "locked_prototype_generation_started",
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
            "locked_prototype_generation_started": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "prototype_generation_started",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_prototype_generation_started",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_prototype_generation_started",
                        "next": "locked_prototype_generation_started",
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
            "waiting_for_app_build": {
                "transitions": [
                    {
                        "name": "complete_generation",
                        "next": "resources_generated",
                        "manual": True,
                    },
                    {
                        "name": "submit_answer",
                        "next": "waiting_for_app_build",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "waiting_for_app_build",
                        "manual": True,
                    },
                    {
                        "name": "manual_approve",
                        "next": "resources_generated",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "waiting_for_app_build",
                        "manual": True,
                    },
                    {
                        "name": "fail_waiting_for_app_build",
                        "next": "locked_waiting_for_app_build",
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
            "locked_waiting_for_app_build": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "waiting_for_app_build",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_waiting_for_app_build",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_waiting_for_app_build",
                        "next": "locked_waiting_for_app_build",
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
            "resources_generated": {
                "transitions": [
                    {
                        "name": "notify_editing_complete",
                        "next": "completed",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.notify_editing_complete",
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
                        "next": "resources_generated",
                        "manual": True,
                    },
                    {
                        "name": "fail_resources_generated",
                        "next": "locked_resources_generated",
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
            "completed": {
                "transitions": [
                    {
                        "name": "complete",
                        "next": "locked_chat_completed",
                        "manual": False,
                    },
                ],
            },
            "locked_chat_completed": {
                "transitions": [
                    {
                        "name": "complete_editing",
                        "next": "completed",
                        "manual": True,
                    }
                ],
            },
        },
    }


ProcessorConfig = {
    "MessageProcessor.notify_editing_started": NotifyEditingStartedMessageConfig,
    "MessageProcessor.notify_editing_requirements_discussion_python": NotifyEditingRequirementsDiscussionPythonMessageConfig,
    "MessageProcessor.notify_started_application_generation": NotifyStartedApplicationGenerationMessageConfig,
    "MessageProcessor.notify_editing_complete": NotifyEditingCompleteMessageConfig,
    "AgentProcessor.process_user_input_2c31_optimized": ProcessUserInput2c31OptimizedAgentConfig,
    "AgentProcessor.process_user_input_9a8e": ProcessUserInput9a8eAgentConfig,
    "AgentProcessor.notify_user_env_deployed_58e2": NotifyUserEnvDeployed58e2AgentConfig,
    "AgentProcessor.edit_app_python": EditAppPythonAgentConfig,
    "FunctionProcessor.not_stage_completed_f57d": NotStageCompletedF57dFunctionConfig,
    "FunctionProcessor.is_stage_completed_e7bf": IsStageCompletedE7bfFunctionConfig,
    "FunctionProcessor.init_chats_for_editing_e8f3": InitChatsForEditingE8f3FunctionConfig,
    "FunctionProcessor.not_stage_completed_f259": NotStageCompletedF259FunctionConfig,
    "FunctionProcessor.is_stage_completed_b809": IsStageCompletedB809FunctionConfig,
    "FunctionProcessor.save_env_file_d2aa": SaveEnvFileD2aaFunctionConfig,
    "FunctionProcessor.delete_files_6818": DeleteFiles6818FunctionConfig,
    "FunctionProcessor.init_setup_workflow_5f06": InitSetupWorkflow5f06FunctionConfig,
}


