"""
BuildGeneralApplicationPythonOptimizedWorkflowConfig Configuration

Generated from config: workflow_configs/configs/build_general_application_python_optimized.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.configs.notify_user_env_deployed_58e2.agent import NotifyUserEnvDeployed58e2AgentConfig
from workflow_config_code.workflows.functions.clone_repo_b60a.function import CloneRepoB60aFunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_e7bf.function import IsStageCompletedE7bfFunctionConfig
from workflow_config_code.workflows.agents.configs.process_user_input_9a8e.agent import ProcessUserInput9a8eAgentConfig
from workflow_config_code.workflows.agents.configs.process_user_input_2c31_optimized_py.agent import ProcessUserInput2c31OptimizedPyAgentConfig
from workflow_config_code.workflows.functions.init_setup_workflow_5f06.function import InitSetupWorkflow5f06FunctionConfig
from workflow_config_code.workflows.agents.configs.generate_app_python.agent import GenerateAppPythonAgentConfig
from workflow_config_code.workflows.messages.notify_requirements_discussion_optimized_py.message import NotifyRequirementsDiscussionOptimizedPyMessageConfig
from workflow_config_code.workflows.messages.notify_project_compiled_f5g6_py.message import NotifyProjectCompiledF5g6PyMessageConfig
from workflow_config_code.workflows.messages.welcome_user_optimized.message import WelcomeUserOptimizedMessageConfig
from workflow_config_code.workflows.functions.not_stage_completed_f57d.function import NotStageCompletedF57dFunctionConfig
from workflow_config_code.workflows.functions.init_chats_d512.function import InitChatsD512FunctionConfig
from workflow_config_code.workflows.functions.save_env_file_d2aa.function import SaveEnvFileD2aaFunctionConfig
from workflow_config_code.workflows.functions.not_stage_completed_f259.function import NotStageCompletedF259FunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_b809.function import IsStageCompletedB809FunctionConfig
from workflow_config_code.workflows.messages.notify_started_application_generation.message import NotifyStartedApplicationGenerationMessageConfig
from workflow_config_code.workflows.functions.delete_files_6818.function import DeleteFiles6818FunctionConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "build_general_application_python_optimized",
        "desc": "Migrated from build_general_application_python",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
                "type": "simple",
                "jsonPath": "$.workflow_name",
                "operation": "EQUALS",
                "value": "build_general_application_python_optimized"
        },
        "states": {
                "initial_state": {
                        "transitions": [
                                {
                                        "name": "initialize",
                                        "next": "initialized",
                                        "manual": False
                                },
                                {
                                        "name": "retry",
                                        "next": "initial_state",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "initial_state",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_initial_state": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "initial_state",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_initial_state",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_initial_state": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_initial_state",
                                        "manual": True
                                }
                        ]
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
                                                                "type": "simple"
                                                        }
                                                ]
                                        }
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
                                                                "type": "simple"
                                                        }
                                                ]
                                        }
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
                                                                "type": "simple"
                                                        }
                                                ]
                                        }
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
                                                                "type": "simple"
                                                        }
                                                ]
                                        }
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
                                                                "type": "simple"
                                                        }
                                                ]
                                        }
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
                                                                "type": "simple"
                                                        }
                                                ]
                                        }
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
                                                                "type": "simple"
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "initialized",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "initialized",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_initialized": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "initialized",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_initialized",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_initialized": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_initialized",
                                        "manual": True
                                }
                        ]
                },
                "building_new_app": {
                        "transitions": [
                                {
                                        "name": "welcome_user",
                                        "next": "greeting_sent",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": WelcomeUserOptimizedMessageConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "building_new_app",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "building_new_app",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_building_new_app": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "building_new_app",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_building_new_app",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_building_new_app": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_building_new_app",
                                        "manual": True
                                }
                        ]
                },
                "greeting_sent": {
                        "transitions": [
                                {
                                        "name": "clone_repo",
                                        "next": "repository_cloned",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": CloneRepoB60aFunctionConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "greeting_sent",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "greeting_sent",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_greeting_sent": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "greeting_sent",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_greeting_sent",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_greeting_sent": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_greeting_sent",
                                        "manual": True
                                }
                        ]
                },
                "repository_cloned": {
                        "transitions": [
                                {
                                        "name": "notify_requirement_discussion",
                                        "next": "app_requirements_requested",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": NotifyRequirementsDiscussionOptimizedPyMessageConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "repository_cloned",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "repository_cloned",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_repository_cloned": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "repository_cloned",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_repository_cloned",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_repository_cloned": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_repository_cloned",
                                        "manual": True
                                }
                        ]
                },
                "app_requirements_requested": {
                        "transitions": [
                                {
                                        "name": "submit_answer",
                                        "next": "app_requirements_requested_submitted_answer",
                                        "manual": True
                                },
                                {
                                        "name": "manual_approve",
                                        "next": "app_requirements_finalized",
                                        "manual": True
                                },
                                {
                                        "name": "rollback",
                                        "next": "app_requirements_requested_submitted_answer",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "app_requirements_requested",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "app_requirements_requested",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_app_requirements_requested": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "app_requirements_requested",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_app_requirements_requested",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_app_requirements_requested": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_app_requirements_requested",
                                        "manual": True
                                }
                        ]
                },
                "app_requirements_requested_submitted_answer": {
                        "transitions": [
                                {
                                        "name": "process_user_input",
                                        "next": "app_requirements_requested_processing",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": ProcessUserInput2c31OptimizedPyAgentConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "app_requirements_requested_submitted_answer",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "app_requirements_requested_submitted_answer",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_app_requirements_requested_submitted_answer": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "app_requirements_requested_submitted_answer",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_app_requirements_requested_submitted_answer",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_app_requirements_requested_submitted_answer": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_app_requirements_requested_submitted_answer",
                                        "manual": True
                                }
                        ]
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
                                                        "name": NotStageCompletedF57dFunctionConfig.get_name(),
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 300000
                                                        }
                                                }
                                        }
                                },
                                {
                                        "name": "process_application_requirement_success",
                                        "next": "app_requirements_finalized",
                                        "manual": False,
                                        "criterion": {
                                                "type": "function",
                                                "function": {
                                                        "name": IsStageCompletedE7bfFunctionConfig.get_name(),
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 300000
                                                        }
                                                }
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "app_requirements_requested_processing",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "app_requirements_requested_processing",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_app_requirements_requested_processing": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "app_requirements_requested_processing",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_app_requirements_requested_processing",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_app_requirements_requested_processing": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_app_requirements_requested_processing",
                                        "manual": True
                                }
                        ]
                },
                "app_requirements_finalized": {
                        "transitions": [
                                {
                                        "name": "ask_about_api",
                                        "next": "proceed_to_saving_files",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": NotifyStartedApplicationGenerationMessageConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "app_requirements_finalized",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "app_requirements_finalized",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_app_requirements_finalized": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "app_requirements_finalized",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_app_requirements_finalized",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_app_requirements_finalized": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_app_requirements_finalized",
                                        "manual": True
                                }
                        ]
                },
                "proceed_to_saving_files": {
                        "transitions": [
                                {
                                        "name": "init_chats",
                                        "next": "env_deployment_notified",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": InitChatsD512FunctionConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "proceed_to_saving_files",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "proceed_to_saving_files",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_proceed_to_saving_files": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "proceed_to_saving_files",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_proceed_to_saving_files",
                                        "manual": True
                                },
                                {
                                        "name": "fail_locked_proceed_to_saving_files",
                                        "next": "locked_locked_proceed_to_saving_files",
                                        "manual": False,
                                        "criterion": {
                                                "type": "group",
                                                "operator": "AND",
                                                "conditions": [
                                                        {
                                                                "type": "simple",
                                                                "jsonPath": "$.failed",
                                                                "operation": "EQUALS",
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_proceed_to_saving_files": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_proceed_to_saving_files",
                                        "manual": True
                                }
                        ]
                },
                "waiting_for_user_deployment_input": {
                        "transitions": [
                                {
                                        "name": "submit_answer",
                                        "next": "env_deployment_notified",
                                        "manual": True
                                },
                                {
                                        "name": "rollback",
                                        "next": "env_deployment_notified",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "waiting_for_user_deployment_input",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "waiting_for_user_deployment_input",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_waiting_for_user_deployment_input": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "waiting_for_user_deployment_input",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_waiting_for_user_deployment_input",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_waiting_for_user_deployment_input": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_waiting_for_user_deployment_input",
                                        "manual": True
                                }
                        ]
                },
                "env_deployment_notified": {
                        "transitions": [
                                {
                                        "name": "process_user_input_1",
                                        "next": "app_requirements_step3_processing",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": ProcessUserInput9a8eAgentConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "env_deployment_notified",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "env_deployment_notified",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_env_deployment_notified": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "env_deployment_notified",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_env_deployment_notified",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_env_deployment_notified": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_env_deployment_notified",
                                        "manual": True
                                }
                        ]
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
                                                        "name": NotStageCompletedF259FunctionConfig.get_name(),
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        }
                                },
                                {
                                        "name": "process_app_setup_3_success",
                                        "next": "deployed_cyoda_env",
                                        "manual": False,
                                        "criterion": {
                                                "type": "function",
                                                "function": {
                                                        "name": IsStageCompletedB809FunctionConfig.get_name(),
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        }
                                },
                                {
                                        "name": "rollback",
                                        "next": "deployed_cyoda_env",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "app_requirements_step3_processing",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "app_requirements_step3_processing",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_app_requirements_step3_processing": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "app_requirements_step3_processing",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_app_requirements_step3_processing",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_app_requirements_step3_processing": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_app_requirements_step3_processing",
                                        "manual": True
                                }
                        ]
                },
                "deployed_cyoda_env": {
                        "transitions": [
                                {
                                        "name": "notify_user_env_deployed",
                                        "next": "prototype_generation_started",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": NotifyUserEnvDeployed58e2AgentConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "deployed_cyoda_env",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "deployed_cyoda_env",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_deployed_cyoda_env": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "deployed_cyoda_env",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_deployed_cyoda_env",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_deployed_cyoda_env": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_deployed_cyoda_env",
                                        "manual": True
                                }
                        ]
                },
                "prototype_generation_started": {
                        "transitions": [
                                {
                                        "name": "start_prototype_generation",
                                        "next": "waiting_for_app_build",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": GenerateAppPythonAgentConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 6000000,
                                                                "retryPolicy": "NONE"
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "prototype_generation_started",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "prototype_generation_started",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_prototype_generation_started": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "prototype_generation_started",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_prototype_generation_started",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_prototype_generation_started": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_prototype_generation_started",
                                        "manual": True
                                }
                        ]
                },
                "waiting_for_app_build": {
                        "transitions": [
                                {
                                        "name": "complete_generation",
                                        "next": "resources_generated",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "waiting_for_app_build",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "waiting_for_app_build",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_waiting_for_app_build": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "waiting_for_app_build",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_waiting_for_app_build",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_waiting_for_app_build": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_waiting_for_app_build",
                                        "manual": True
                                }
                        ]
                },
                "resources_generated": {
                        "transitions": [
                                {
                                        "name": "workflow_completed",
                                        "next": "save_env_file",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": NotifyProjectCompiledF5g6PyMessageConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant"
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "resources_generated",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "resources_generated",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_resources_generated": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "resources_generated",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_resources_generated",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_resources_generated": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_resources_generated",
                                        "manual": True
                                }
                        ]
                },
                "save_env_file": {
                        "transitions": [
                                {
                                        "name": "save_env_file",
                                        "next": "delete_files",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": SaveEnvFileD2aaFunctionConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "save_env_file",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "save_env_file",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_save_env_file": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "save_env_file",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_save_env_file",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_save_env_file": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_save_env_file",
                                        "manual": True
                                }
                        ]
                },
                "delete_files": {
                        "transitions": [
                                {
                                        "name": "delete_files",
                                        "next": "launch_setup_assistant",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": DeleteFiles6818FunctionConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "delete_files",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "delete_files",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_delete_files": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "delete_files",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_delete_files",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_delete_files": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_delete_files",
                                        "manual": True
                                }
                        ]
                },
                "launch_setup_assistant": {
                        "transitions": [
                                {
                                        "name": "launch_setup_assistant",
                                        "next": "completed",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": InitSetupWorkflow5f06FunctionConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant",
                                                                "responseTimeoutMs": 900000
                                                        }
                                                }
                                        ]
                                },
                                {
                                        "name": "retry",
                                        "next": "launch_setup_assistant",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "launch_setup_assistant",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_launch_setup_assistant": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "launch_setup_assistant",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_launch_setup_assistant",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_launch_setup_assistant": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_launch_setup_assistant",
                                        "manual": True
                                }
                        ]
                },
                "completed": {
                        "transitions": [
                                {
                                        "name": "lock_chat",
                                        "next": "locked_chat",
                                        "manual": False
                                },
                                {
                                        "name": "retry",
                                        "next": "completed",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                },
                                {
                                        "name": "retry",
                                        "next": "completed",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_completed": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "completed",
                                        "manual": True
                                },
                                {
                                        "name": "retry",
                                        "next": "locked_completed",
                                        "manual": True
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
                                                                "value": True
                                                        }
                                                ]
                                        }
                                }
                        ]
                },
                "locked_locked_completed": {
                        "transitions": [
                                {
                                        "name": "unlock",
                                        "next": "locked_completed",
                                        "manual": True
                                }
                        ]
                }
        }
}
