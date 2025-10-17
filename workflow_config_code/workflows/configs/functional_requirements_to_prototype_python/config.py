"""
FunctionalRequirementsToPrototypePythonWorkflowConfig Configuration

Generated from config: workflow_configs/configs/functional_requirements_to_prototype_python.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.configs.generate_controller_d4e3_py.agent import GenerateControllerD4e3PyAgentConfig
from workflow_config_code.workflows.functions.save_env_file_d2aa.function import SaveEnvFileD2aaFunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_discuss_prototype_0000.function import IsStageCompletedDiscussPrototype0000FunctionConfig
from workflow_config_code.workflows.messages.ask_to_confirm_migration_208e.message import AskToConfirmMigration208eMessageConfig
from workflow_config_code.workflows.functions.delete_files_6818.function import DeleteFiles6818FunctionConfig
from workflow_config_code.workflows.functions.not_stage_completed_discuss_prototype_0000.function import NotStageCompletedDiscussPrototype0000FunctionConfig
from workflow_config_code.workflows.agents.configs.process_prototype_discussion_0000_py.agent import ProcessPrototypeDiscussion0000PyAgentConfig
from workflow_config_code.workflows.messages.notify_project_compiled_f5g6_py.message import NotifyProjectCompiledF5g6PyMessageConfig
from workflow_config_code.workflows.functions.init_setup_workflow_5f06.function import InitSetupWorkflow5f06FunctionConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "functional_requirements_to_prototype_python",
        "desc": "Complete workflow to transform functional requirements into a working application",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "functional_requirements_to_prototype_python",
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "start_save_functional_requirements",
                        "next": "generate_controller",
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
                ],
            },
            "generate_controller": {
                "transitions": [
                    {
                        "name": "controller_generated",
                        "next": "waiting_for_app_build",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.generate_controller_d4e3_py",
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 6000000,
                                    "retryPolicy": "NONE",
                                },
                            },
                        ],
                    },
                    {
                        "name": "retry",
                        "next": "generate_controller",
                        "manual": True,
                    },
                    {
                        "name": "fail_generate_controller",
                        "next": "locked_generate_controller",
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
            "locked_generate_controller": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "generate_controller",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_generate_controller",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_generate_controller",
                        "next": "locked_locked_generate_controller",
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
            "locked_locked_generate_controller": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_generate_controller",
                        "manual": True,
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
                        "next": "locked_locked_waiting_for_app_build",
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
            "locked_locked_waiting_for_app_build": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_waiting_for_app_build",
                        "manual": True,
                    },
                ],
            },
            "resources_generated": {
                "transitions": [
                    {
                        "name": "workflow_completed",
                        "next": "waiting_prototype_discussion_requested",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.notify_project_compiled_f5g6_py",
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
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
            "locked_resources_generated": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "resources_generated",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_resources_generated",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_resources_generated",
                        "next": "locked_locked_resources_generated",
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
            "locked_locked_resources_generated": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_resources_generated",
                        "manual": True,
                    },
                ],
            },
            "waiting_prototype_discussion_requested": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "prototype_discussion_requested_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "manual_approve",
                        "next": "prototype_discussion_completed",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "prototype_discussion_requested_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "rollback_to_initial_state",
                        "next": "initial_state",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "waiting_prototype_discussion_requested",
                        "manual": True,
                    },
                    {
                        "name": "fail_waiting_prototype_discussion_requested",
                        "next": "locked_waiting_prototype_discussion_requested",
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
            "locked_waiting_prototype_discussion_requested": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "waiting_prototype_discussion_requested",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_waiting_prototype_discussion_requested",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_waiting_prototype_discussion_requested",
                        "next": "locked_locked_waiting_prototype_discussion_requested",
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
            "locked_locked_waiting_prototype_discussion_requested": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_waiting_prototype_discussion_requested",
                        "manual": True,
                    },
                ],
            },
            "prototype_discussion_requested_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "prototype_discussion_requested_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_prototype_discussion_0000_py",
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
                        "next": "prototype_discussion_requested_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_prototype_discussion_requested_submitted_answer",
                        "next": "locked_prototype_discussion_requested_submitted_answer",
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
            "locked_prototype_discussion_requested_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "prototype_discussion_requested_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_prototype_discussion_requested_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_prototype_discussion_requested_submitted_answer",
                        "next": "locked_locked_prototype_discussion_requested_submitted_answer",
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
            "locked_locked_prototype_discussion_requested_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_prototype_discussion_requested_submitted_answer",
                        "manual": True,
                    },
                ],
            },
            "prototype_discussion_requested_processing": {
                "transitions": [
                    {
                        "name": "process_configs_discussion_processing",
                        "next": "waiting_prototype_discussion_requested",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.not_stage_completed_discuss_prototype_0000",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000,
                                },
                            },
                        },
                    },
                    {
                        "name": "prototype_configs_discussion_success",
                        "next": "prototype_discussion_completed",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_stage_completed_discuss_prototype_0000",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000,
                                },
                            },
                        },
                    },
                    {
                        "name": "retry",
                        "next": "prototype_discussion_requested_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_prototype_discussion_requested_processing",
                        "next": "locked_prototype_discussion_requested_processing",
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
            "locked_prototype_discussion_requested_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "prototype_discussion_requested_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_prototype_discussion_requested_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_prototype_discussion_requested_processing",
                        "next": "locked_locked_prototype_discussion_requested_processing",
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
            "locked_locked_prototype_discussion_requested_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_prototype_discussion_requested_processing",
                        "manual": True,
                    },
                ],
            },
            "prototype_discussion_completed": {
                "transitions": [
                    {
                        "name": "ask_to_confirm_migration",
                        "next": "save_env_file",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.ask_to_confirm_migration_208e",
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
                        "next": "prototype_discussion_completed",
                        "manual": True,
                    },
                    {
                        "name": "fail_prototype_discussion_completed",
                        "next": "locked_prototype_discussion_completed",
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
            "locked_prototype_discussion_completed": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "prototype_discussion_completed",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_prototype_discussion_completed",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_prototype_discussion_completed",
                        "next": "locked_locked_prototype_discussion_completed",
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
            "locked_locked_prototype_discussion_completed": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_prototype_discussion_completed",
                        "manual": True,
                    },
                ],
            },
            "save_env_file": {
                "transitions": [
                    {
                        "name": "save_env_file",
                        "next": "delete_files",
                        "manual": False,
                        "processors": [
                            {
                                "name": "FunctionProcessor.save_env_file_d2aa",
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
                        "next": "save_env_file",
                        "manual": True,
                    },
                    {
                        "name": "fail_save_env_file",
                        "next": "locked_save_env_file",
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
            "locked_save_env_file": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "save_env_file",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_save_env_file",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_save_env_file",
                        "next": "locked_locked_save_env_file",
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
            "locked_locked_save_env_file": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_save_env_file",
                        "manual": True,
                    },
                ],
            },
            "delete_files": {
                "transitions": [
                    {
                        "name": "delete_files",
                        "next": "launch_setup_assistant",
                        "manual": False,
                        "processors": [
                            {
                                "name": "FunctionProcessor.delete_files_6818",
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
                        "next": "delete_files",
                        "manual": True,
                    },
                    {
                        "name": "fail_delete_files",
                        "next": "locked_delete_files",
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
            "locked_delete_files": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "delete_files",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_delete_files",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_delete_files",
                        "next": "locked_locked_delete_files",
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
            "locked_locked_delete_files": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_delete_files",
                        "manual": True,
                    },
                ],
            },
            "launch_setup_assistant": {
                "transitions": [
                    {
                        "name": "launch_setup_assistant",
                        "next": "launched_setup_assistant",
                        "manual": False,
                        "processors": [
                            {
                                "name": "FunctionProcessor.init_setup_workflow_5f06",
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
                        "next": "launch_setup_assistant",
                        "manual": True,
                    },
                    {
                        "name": "fail_launch_setup_assistant",
                        "next": "locked_launch_setup_assistant",
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
            "locked_launch_setup_assistant": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "launch_setup_assistant",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_launch_setup_assistant",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_launch_setup_assistant",
                        "next": "locked_locked_launch_setup_assistant",
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
            "locked_locked_launch_setup_assistant": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_launch_setup_assistant",
                        "manual": True,
                    },
                ],
            },
            "launched_setup_assistant": {
                "transitions": [
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False,
                    },
                    {
                        "name": "retry",
                        "next": "launched_setup_assistant",
                        "manual": True,
                    },
                    {
                        "name": "fail_launched_setup_assistant",
                        "next": "locked_launched_setup_assistant",
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
            "locked_launched_setup_assistant": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "launched_setup_assistant",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_launched_setup_assistant",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_launched_setup_assistant",
                        "next": "locked_locked_launched_setup_assistant",
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
            "locked_locked_launched_setup_assistant": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_launched_setup_assistant",
                        "manual": True,
                    },
                ],
            },
        },
    }
