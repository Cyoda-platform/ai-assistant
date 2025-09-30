"""
FunctionalRequirementsToPrototypeJavaWorkflowConfig Configuration

Configuration data for the functional requirements to application workflow.
"""

from typing import Any, Dict, Callable

from common.config import const
from workflow_config_code.workflows.agents.compile_project_f6g5.agent import CompileProjectF6g5AgentConfig
from workflow_config_code.workflows.agents.fix_compilation_errors_i1j2.agent import FixCompilationErrorsI1j2AgentConfig
from workflow_config_code.workflows.agents.generate_controller_d4e3_py.agent import GenerateControllerD4e3PyAgentConfig
from workflow_config_code.workflows.agents.process_prototype_discussion_0000.agent import \
    ProcessPrototypeDiscussion0000AgentConfig
from workflow_config_code.workflows.agents.process_prototype_discussion_0000_py.agent import \
    ProcessPrototypeDiscussion0000PyAgentConfig
from workflow_config_code.workflows.messages.ask_to_confirm_migration_208e.message import AskToConfirmMigration208eMessageConfig
from workflow_config_code.workflows.agents.generate_controller_d4e3.agent import GenerateControllerD4e3AgentConfig
from workflow_config_code.workflows.agents.enhance_processors_g6h7.agent import EnhanceProcessorsG6h7AgentConfig
from workflow_config_code.workflows.messages.notify_processors_enhanced_g7h8.message import \
    NotifyProcessorsEnhancedG7h8MessageConfig
from workflow_config_code.workflows.messages.notify_project_compiled_f5g6_py.message import \
    NotifyProjectCompiledF5g6PyMessageConfig
from workflow_config_code.workflows.functions.delete_files_6818.function import DeleteFiles6818FunctionConfig
from workflow_config_code.workflows.functions.init_setup_workflow_5f06.function import InitSetupWorkflow5f06FunctionConfig
from workflow_config_code.workflows.functions.is_stage_completed_discuss_prototype_0000.function import \
    IsStageCompletedDiscussPrototype0000FunctionConfig
from workflow_config_code.workflows.functions.not_stage_completed_discuss_prototype_0000.function import \
    NotStageCompletedDiscussPrototype0000FunctionConfig
from workflow_config_code.workflows.functions.run_compilation_h8i9.function import RunCompilationH8i9FunctionConfig
from workflow_config_code.workflows.messages.notify_project_compiled_f5g6.message import NotifyProjectCompiledF5g6MessageConfig
from workflow_config_code.workflows.functions.save_env_file_d2aa.function import SaveEnvFileD2aaFunctionConfig


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
            "value": "functional_requirements_to_prototype_python"
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "start_save_functional_requirements",
                        "next": "generate_controller",
                        "manual": False
                    }
                ]
            },
            "generate_controller": {
                "transitions": [
                    {
                        "name": "controller_generated",
                        "next": "waiting_for_app_build",
                        "manual": False,
                        "processors": [
                            {
                                "name": GenerateControllerD4e3PyAgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 6000000,
                                    "retryPolicy": "NONE"
                                }
                            }
                        ]
                    }
                ]
            },
            "waiting_for_app_build": {
                "transitions": [
                    {
                        "name": "complete_generation",
                        "next": "resources_generated",
                        "manual": True
                    }
                ]
            },
            "resources_generated": {
                "transitions": [
                    {
                        "name": "workflow_completed",
                        "next": "waiting_prototype_discussion_requested",
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
                    }
                ]
            },
            "waiting_prototype_discussion_requested": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "prototype_discussion_requested_submitted_answer",
                        "manual": True
                    },
                    {
                        "name": "manual_approve",
                        "next": "prototype_discussion_completed",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "prototype_discussion_requested_submitted_answer",
                        "manual": True
                    },
                    {
                        "name": "rollback_to_initial_state",
                        "next": "initial_state",
                        "manual": True
                    }
                ]
            },
            "prototype_discussion_requested_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "prototype_discussion_requested_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessPrototypeDiscussion0000PyAgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000
                                }
                            }
                        ]
                    }
                ]
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
                                "name": NotStageCompletedDiscussPrototype0000FunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000
                                }
                            }
                        }
                    },
                    {
                        "name": "prototype_configs_discussion_success",
                        "next": "prototype_discussion_completed",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsStageCompletedDiscussPrototype0000FunctionConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000
                                }
                            }
                        }
                    }
                ]
            },
            "prototype_discussion_completed": {
                "transitions": [
                    {
                        "name": "ask_to_confirm_migration",
                        "next": "save_env_file",
                        "manual": False,
                        "processors": [
                            {
                                "name": AskToConfirmMigration208eMessageConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000
                                }
                            }
                        ]
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
                    }
                ]
            },
            "launch_setup_assistant": {
                "transitions": [
                    {
                        "name": "launch_setup_assistant",
                        "next": "launched_setup_assistant",
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
                    }
                ]
            },
            "launched_setup_assistant": {
                "transitions": [
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False
                    }
                ]
            }
        }
    }
