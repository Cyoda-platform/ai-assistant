"""
BuildGeneralApplicationJavaWorkflowConfig Configuration

Generated from config: workflow_configs/configs/build_general_application_java.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.messages.welcome_user_25fc.message import WelcomeUser25fcMessageConfig
from workflow_config_code.workflows.messages.notify_env_deployment_start_c5d6.message import NotifyEnvDeploymentStartC5d6MessageConfig
from workflow_config_code.workflows.agents.configs.process_user_input_cd43.agent import ProcessUserInputCd43AgentConfig
from workflow_config_code.workflows.functions.not_stage_completed_5e0e.function import NotStageCompleted5e0eFunctionConfig
from workflow_config_code.workflows.messages.notify_requirement_discussion_a1b3.message import NotifyRequirementDiscussionA1b3MessageConfig
from workflow_config_code.workflows.functions.not_stage_completed_f259.function import NotStageCompletedF259FunctionConfig
from workflow_config_code.workflows.agents.configs.define_functional_requirements_8ee2.agent import DefineFunctionalRequirements8ee2AgentConfig
from workflow_config_code.workflows.agents.configs.notify_user_env_deployed_58e2.agent import NotifyUserEnvDeployed58e2AgentConfig
from workflow_config_code.workflows.agents.configs.process_initial_question_cd33.agent import ProcessInitialQuestionCd33AgentConfig
from workflow_config_code.workflows.agents.configs.process_user_input_9a8e.agent import ProcessUserInput9a8eAgentConfig
from workflow_config_code.workflows.messages.notify_prototype_generation_0000.message import NotifyPrototypeGeneration0000MessageConfig
from workflow_config_code.workflows.functions.clone_repo_b60a.function import CloneRepoB60aFunctionConfig
from workflow_config_code.workflows.messages.notify_generated_original_requirements_b94e.message import NotifyGeneratedOriginalRequirementsB94eMessageConfig
from workflow_config_code.workflows.functions.init_chats_d512.function import InitChatsD512FunctionConfig
from workflow_config_code.workflows.agents.configs.process_user_input_2c31.agent import ProcessUserInput2c31AgentConfig
from workflow_config_code.workflows.messages.ask_about_api_d91f.message import AskAboutApiD91fMessageConfig
from workflow_config_code.workflows.functions.is_stage_completed_8a02.function import IsStageCompleted8a02FunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_b809.function import IsStageCompletedB809FunctionConfig
from workflow_config_code.workflows.functions.generate_prototype_sketch_2269.function import GeneratePrototypeSketch2269FunctionConfig
from workflow_config_code.workflows.messages.ask_about_api_063f.message import AskAboutApi063fMessageConfig
from workflow_config_code.workflows.functions.is_stage_completed_e7bf.function import IsStageCompletedE7bfFunctionConfig
from workflow_config_code.workflows.functions.not_stage_completed_f57d.function import NotStageCompletedF57dFunctionConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "build_general_application_java",
        "desc": "Migrated from build_general_application_java",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "build_general_application_java",
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
            "initialized": {
                "transitions": [
                    {
                        "name": "build_new_app",
                        "next": "building_new_app",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "name": "build_new_app_criteria",
                            "operator": "AND",
                            "parameters": [
                                {
                                    "jsonPath": "resume_transition",
                                    "operatorType": "IEQUALS",
                                    "value": "build_new_app",
                                    "type": "simple",
                                },
                            ],
                        },
                    },
                    {
                        "name": "discuss_functional_requirements",
                        "next": "chats_initialized",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "name": "discuss_functional_requirements_criteria",
                            "operator": "AND",
                            "parameters": [
                                {
                                    "jsonPath": "resume_transition",
                                    "operatorType": "IEQUALS",
                                    "value": "discuss_functional_requirements",
                                    "type": "simple",
                                },
                            ],
                        },
                    },
                    {
                        "name": "edit_functional_requirements",
                        "next": "functional_requirements_specified",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "name": "edit_functional_requirements_criteria",
                            "operator": "AND",
                            "parameters": [
                                {
                                    "jsonPath": "resume_transition",
                                    "operatorType": "IEQUALS",
                                    "value": "edit_functional_requirements",
                                    "type": "simple",
                                },
                            ],
                        },
                    },
                    {
                        "name": "prototype_discussion_requested",
                        "next": "notified_generated_workflows",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "name": "prototype_discussion_requested_criteria",
                            "operator": "AND",
                            "parameters": [
                                {
                                    "jsonPath": "resume_transition",
                                    "operatorType": "IEQUALS",
                                    "value": "prototype_discussion_requested",
                                    "type": "simple",
                                },
                            ],
                        },
                    },
                    {
                        "name": "resume_migration",
                        "next": "prototype_generation_started",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "name": "resume_migration_criteria",
                            "operator": "AND",
                            "parameters": [
                                {
                                    "jsonPath": "resume_transition",
                                    "operatorType": "IEQUALS",
                                    "value": "resume_migration",
                                    "type": "simple",
                                },
                            ],
                        },
                    },
                    {
                        "name": "resume_prototype_cyoda_workflow",
                        "next": "notified_generated_workflows",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "name": "resume_prototype_cyoda_workflow_criteria",
                            "operator": "AND",
                            "parameters": [
                                {
                                    "jsonPath": "resume_transition",
                                    "operatorType": "IEQUALS",
                                    "value": "resume_prototype_cyoda_workflow",
                                    "type": "simple",
                                },
                            ],
                        },
                    },
                    {
                        "name": "resume_post_app_build_steps",
                        "next": "prototype_generation_started",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "name": "resume_post_app_build_steps_criteria",
                            "operator": "AND",
                            "parameters": [
                                {
                                    "jsonPath": "resume_transition",
                                    "operatorType": "IEQUALS",
                                    "value": "resume_post_app_build_steps",
                                    "type": "simple",
                                },
                            ],
                        },
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
                        "next": "locked_locked_initialized",
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
            "locked_locked_initialized": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_initialized",
                        "manual": True,
                    },
                ],
            },
            "building_new_app": {
                "transitions": [
                    {
                        "name": "welcome_user",
                        "next": "greeting_sent",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.welcome_user_25fc",
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
                        "next": "building_new_app",
                        "manual": True,
                    },
                    {
                        "name": "fail_building_new_app",
                        "next": "locked_building_new_app",
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
            "locked_building_new_app": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "building_new_app",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_building_new_app",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_building_new_app",
                        "next": "locked_locked_building_new_app",
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
            "locked_locked_building_new_app": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_building_new_app",
                        "manual": True,
                    },
                ],
            },
            "greeting_sent": {
                "transitions": [
                    {
                        "name": "clone_repo",
                        "next": "repository_cloned",
                        "manual": False,
                        "processors": [
                            {
                                "name": "FunctionProcessor.clone_repo_b60a",
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
                        "next": "greeting_sent",
                        "manual": True,
                    },
                    {
                        "name": "fail_greeting_sent",
                        "next": "locked_greeting_sent",
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
            "locked_greeting_sent": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "greeting_sent",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_greeting_sent",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_greeting_sent",
                        "next": "locked_locked_greeting_sent",
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
            "locked_locked_greeting_sent": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_greeting_sent",
                        "manual": True,
                    },
                ],
            },
            "repository_cloned": {
                "transitions": [
                    {
                        "name": "init_chats",
                        "next": "generated_original_requirements",
                        "manual": False,
                        "processors": [
                            {
                                "name": "FunctionProcessor.init_chats_d512",
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
                        "next": "repository_cloned",
                        "manual": True,
                    },
                    {
                        "name": "fail_repository_cloned",
                        "next": "locked_repository_cloned",
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
            "locked_repository_cloned": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "repository_cloned",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_repository_cloned",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_repository_cloned",
                        "next": "locked_locked_repository_cloned",
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
            "locked_locked_repository_cloned": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_repository_cloned",
                        "manual": True,
                    },
                ],
            },
            "generated_original_requirements": {
                "transitions": [
                    {
                        "name": "notify_generated_original_requirements",
                        "next": "notified_generated_original_requirements_saved",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.notify_generated_original_requirements_b94e",
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
                        "next": "generated_original_requirements",
                        "manual": True,
                    },
                    {
                        "name": "fail_generated_original_requirements",
                        "next": "locked_generated_original_requirements",
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
            "locked_generated_original_requirements": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "generated_original_requirements",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_generated_original_requirements",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_generated_original_requirements",
                        "next": "locked_locked_generated_original_requirements",
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
            "locked_locked_generated_original_requirements": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_generated_original_requirements",
                        "manual": True,
                    },
                ],
            },
            "notified_generated_original_requirements_saved": {
                "transitions": [
                    {
                        "name": "notify_requirement_discussion",
                        "next": "notified_generated_original_requirements",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.notify_requirement_discussion_a1b3",
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
                        "next": "notified_generated_original_requirements_saved",
                        "manual": True,
                    },
                    {
                        "name": "fail_notified_generated_original_requirements_saved",
                        "next": "locked_notified_generated_original_requirements_saved",
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
            "locked_notified_generated_original_requirements_saved": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "notified_generated_original_requirements_saved",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_notified_generated_original_requirements_saved",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_notified_generated_original_requirements_saved",
                        "next": "locked_locked_notified_generated_original_requirements_saved",
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
            "locked_locked_notified_generated_original_requirements_saved": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_notified_generated_original_requirements_saved",
                        "manual": True,
                    },
                ],
            },
            "notified_generated_original_requirements": {
                "transitions": [
                    {
                        "name": "process_initial_question",
                        "next": "app_requirements_requested",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_initial_question_cd33",
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
                        "next": "notified_generated_original_requirements",
                        "manual": True,
                    },
                    {
                        "name": "fail_notified_generated_original_requirements",
                        "next": "locked_notified_generated_original_requirements",
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
            "locked_notified_generated_original_requirements": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "notified_generated_original_requirements",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_notified_generated_original_requirements",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_notified_generated_original_requirements",
                        "next": "locked_locked_notified_generated_original_requirements",
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
            "locked_locked_notified_generated_original_requirements": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_notified_generated_original_requirements",
                        "manual": True,
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
                                "name": "AgentProcessor.process_user_input_2c31",
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
                        "next": "locked_locked_app_requirements_requested_submitted_answer",
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
            "locked_locked_app_requirements_requested_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_requested_submitted_answer",
                        "manual": True,
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
                        "next": "locked_locked_app_requirements_requested_processing",
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
            "locked_locked_app_requirements_requested_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_requested_processing",
                        "manual": True,
                    },
                ],
            },
            "app_requirements_finalized": {
                "transitions": [
                    {
                        "name": "ask_about_api",
                        "next": "proceeded_to_functional_requirements",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.ask_about_api_063f",
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
                        "next": "locked_locked_app_requirements_finalized",
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
            "locked_locked_app_requirements_finalized": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_app_requirements_finalized",
                        "manual": True,
                    },
                ],
            },
            "proceeded_to_functional_requirements": {
                "transitions": [
                    {
                        "name": "save_additional_requirements_files",
                        "next": "saved_additional_requirements_files",
                        "manual": False,
                        "processors": [
                            {
                                "name": "FunctionProcessor.init_chats_d512",
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
                        "next": "proceeded_to_functional_requirements",
                        "manual": True,
                    },
                    {
                        "name": "fail_proceeded_to_functional_requirements",
                        "next": "locked_proceeded_to_functional_requirements",
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
            "locked_proceeded_to_functional_requirements": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "proceeded_to_functional_requirements",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_proceeded_to_functional_requirements",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_proceeded_to_functional_requirements",
                        "next": "locked_locked_proceeded_to_functional_requirements",
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
            "locked_locked_proceeded_to_functional_requirements": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_proceeded_to_functional_requirements",
                        "manual": True,
                    },
                ],
            },
            "saved_additional_requirements_files": {
                "transitions": [
                    {
                        "name": "define_functional_requirements",
                        "next": "waiting_for_requirements_gen",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.define_functional_requirements_8ee2",
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000,
                                    "retryPolicy": "NONE",
                                },
                            },
                        ],
                    },
                    {
                        "name": "retry",
                        "next": "saved_additional_requirements_files",
                        "manual": True,
                    },
                    {
                        "name": "fail_saved_additional_requirements_files",
                        "next": "locked_saved_additional_requirements_files",
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
            "locked_saved_additional_requirements_files": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "saved_additional_requirements_files",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_saved_additional_requirements_files",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_saved_additional_requirements_files",
                        "next": "locked_locked_saved_additional_requirements_files",
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
            "locked_locked_saved_additional_requirements_files": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_saved_additional_requirements_files",
                        "manual": True,
                    },
                ],
            },
            "waiting_for_requirements_gen": {
                "transitions": [
                    {
                        "name": "complete_generation",
                        "next": "functional_requirements_specified",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "waiting_for_requirements_gen",
                        "manual": True,
                    },
                    {
                        "name": "fail_waiting_for_requirements_gen",
                        "next": "locked_waiting_for_requirements_gen",
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
            "locked_waiting_for_requirements_gen": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "waiting_for_requirements_gen",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_waiting_for_requirements_gen",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_waiting_for_requirements_gen",
                        "next": "locked_locked_waiting_for_requirements_gen",
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
            "locked_locked_waiting_for_requirements_gen": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_waiting_for_requirements_gen",
                        "manual": True,
                    },
                ],
            },
            "functional_requirements_specified": {
                "transitions": [
                    {
                        "name": "ask_about_api",
                        "next": "api_inquired",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.ask_about_api_d91f",
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
                        "next": "functional_requirements_specified",
                        "manual": True,
                    },
                    {
                        "name": "fail_functional_requirements_specified",
                        "next": "locked_functional_requirements_specified",
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
            "locked_functional_requirements_specified": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "functional_requirements_specified",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_functional_requirements_specified",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_functional_requirements_specified",
                        "next": "locked_locked_functional_requirements_specified",
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
            "locked_locked_functional_requirements_specified": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_functional_requirements_specified",
                        "manual": True,
                    },
                ],
            },
            "api_inquired": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "api_inquired_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "manual_approve",
                        "next": "env_deployment_started",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "api_inquired_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "api_inquired",
                        "manual": True,
                    },
                    {
                        "name": "fail_api_inquired",
                        "next": "locked_api_inquired",
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
            "locked_api_inquired": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "api_inquired",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_api_inquired",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_api_inquired",
                        "next": "locked_locked_api_inquired",
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
            "locked_locked_api_inquired": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_api_inquired",
                        "manual": True,
                    },
                ],
            },
            "api_inquired_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "api_inquired_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.process_user_input_cd43",
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
                        "next": "api_inquired_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_api_inquired_submitted_answer",
                        "next": "locked_api_inquired_submitted_answer",
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
            "locked_api_inquired_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "api_inquired_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_api_inquired_submitted_answer",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_api_inquired_submitted_answer",
                        "next": "locked_locked_api_inquired_submitted_answer",
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
            "locked_locked_api_inquired_submitted_answer": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_api_inquired_submitted_answer",
                        "manual": True,
                    },
                ],
            },
            "api_inquired_processing": {
                "transitions": [
                    {
                        "name": "process_api_inquiry_processing",
                        "next": "api_inquired",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.not_stage_completed_5e0e",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000,
                                },
                            },
                        },
                    },
                    {
                        "name": "process_api_inquiry_success",
                        "next": "env_deployment_started",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": "FunctionProcessor.is_stage_completed_8a02",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000,
                                },
                            },
                        },
                    },
                    {
                        "name": "retry",
                        "next": "api_inquired_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_api_inquired_processing",
                        "next": "locked_api_inquired_processing",
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
            "locked_api_inquired_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "api_inquired_processing",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_api_inquired_processing",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_api_inquired_processing",
                        "next": "locked_locked_api_inquired_processing",
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
            "locked_locked_api_inquired_processing": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_api_inquired_processing",
                        "manual": True,
                    },
                ],
            },
            "waiting_for_user_deployment_input": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "env_deployment_started",
                        "manual": True,
                    },
                    {
                        "name": "rollback",
                        "next": "env_deployment_started",
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
                        "next": "locked_locked_waiting_for_user_deployment_input",
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
            "locked_locked_waiting_for_user_deployment_input": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_waiting_for_user_deployment_input",
                        "manual": True,
                    },
                ],
            },
            "env_deployment_started": {
                "transitions": [
                    {
                        "name": "notify_env_deployment_start",
                        "next": "env_deployment_notified",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.notify_env_deployment_start_c5d6",
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
                        "next": "env_deployment_started",
                        "manual": True,
                    },
                    {
                        "name": "fail_env_deployment_started",
                        "next": "locked_env_deployment_started",
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
            "locked_env_deployment_started": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "env_deployment_started",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_env_deployment_started",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_env_deployment_started",
                        "next": "locked_locked_env_deployment_started",
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
            "locked_locked_env_deployment_started": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_env_deployment_started",
                        "manual": True,
                    },
                ],
            },
            "env_deployment_notified": {
                "transitions": [
                    {
                        "name": "process_user_input",
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
                        "next": "locked_locked_env_deployment_notified",
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
            "locked_locked_env_deployment_notified": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_env_deployment_notified",
                        "manual": True,
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
                ],
            },
            "deployed_cyoda_env": {
                "transitions": [
                    {
                        "name": "notify_user_env_deployed",
                        "next": "api_discussion_completed",
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
                        "next": "locked_locked_deployed_cyoda_env",
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
            "locked_locked_deployed_cyoda_env": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_deployed_cyoda_env",
                        "manual": True,
                    },
                ],
            },
            "api_discussion_completed": {
                "transitions": [
                    {
                        "name": "notify_prototype_generation_started",
                        "next": "prototype_generation_started",
                        "manual": False,
                        "processors": [
                            {
                                "name": "MessageProcessor.notify_prototype_generation_0000",
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
                        "next": "api_discussion_completed",
                        "manual": True,
                    },
                    {
                        "name": "fail_api_discussion_completed",
                        "next": "locked_api_discussion_completed",
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
            "locked_api_discussion_completed": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "api_discussion_completed",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_api_discussion_completed",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_api_discussion_completed",
                        "next": "locked_locked_api_discussion_completed",
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
            "locked_locked_api_discussion_completed": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_api_discussion_completed",
                        "manual": True,
                    },
                ],
            },
            "prototype_generation_started": {
                "transitions": [
                    {
                        "name": "generate_prototype",
                        "next": "completed",
                        "manual": False,
                        "processors": [
                            {
                                "name": "FunctionProcessor.generate_prototype_sketch_2269",
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
                        "next": "locked_locked_prototype_generation_started",
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
            "locked_locked_prototype_generation_started": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_prototype_generation_started",
                        "manual": True,
                    },
                ],
            },
            "completed": {
                "transitions": [
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False,
                    },
                    {
                        "name": "retry",
                        "next": "completed",
                        "manual": True,
                    },
                    {
                        "name": "fail_completed",
                        "next": "locked_completed",
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
            "locked_completed": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "completed",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_completed",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_completed",
                        "next": "locked_locked_completed",
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
            "locked_locked_completed": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_completed",
                        "manual": True,
                    },
                ],
            },
        },
    }
