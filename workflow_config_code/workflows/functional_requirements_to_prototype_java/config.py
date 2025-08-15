"""
FunctionalRequirementsToPrototypeJavaWorkflowConfig Configuration

Configuration data for the functional requirements to application workflow.
"""

from typing import Any, Dict, Callable

from workflow_config_code.agents.compile_project_f6g5.agent import CompileProjectF6g5AgentConfig
from workflow_config_code.agents.generate_tests_for_processors.agent import GenerateTestsForProcessorsAgentConfig
from workflow_config_code.agents.implement_processors_business_logic_g6h7.agent import \
    ImplementProcessorsBusinessLogicG6h7AgentConfig
from workflow_config_code.agents.process_prototype_discussion_0000.agent import \
    ProcessPrototypeDiscussion0000AgentConfig
from workflow_config_code.agents.process_user_input_2185.agent import ProcessUserInput2185AgentConfig
from workflow_config_code.agents.save_functional_requirements_f2a1.agent import \
    SaveFunctionalRequirementsF2a1AgentConfig
from workflow_config_code.messages.ask_to_confirm_migration_208e.message import AskToConfirmMigration208eMessageConfig
from workflow_config_code.messages.notify_saved_fun_req_a1b2.message import NotifySavedFunReqA1b2MessageConfig
from workflow_config_code.agents.generate_controller_d4e3.agent import GenerateControllerD4e3AgentConfig
from workflow_config_code.messages.notify_controller_generated_d3e4.message import \
    NotifyControllerGeneratedD3e4MessageConfig
from workflow_config_code.agents.generate_processors_and_criteria_e5f4.agent import \
    GenerateProcessorsAndCriteriaE5f4AgentConfig
from workflow_config_code.messages.notify_processors_generated_e4f5.message import \
    NotifyProcessorsGeneratedE4f5MessageConfig
from workflow_config_code.agents.enhance_processors_g6h7.agent import EnhanceProcessorsG6h7AgentConfig
from workflow_config_code.messages.notify_processors_enhanced_g7h8.message import \
    NotifyProcessorsEnhancedG7h8MessageConfig
from workflow_config_code.tools.delete_files_6818.tool import DeleteFiles6818ToolConfig
from workflow_config_code.tools.init_setup_workflow_5f06.tool import InitSetupWorkflow5f06ToolConfig
from workflow_config_code.tools.is_stage_completed_c00a.tool import IsStageCompletedC00aToolConfig
from workflow_config_code.tools.is_stage_completed_discuss_prototype_0000.tool import \
    IsStageCompletedDiscussPrototype0000ToolConfig
from workflow_config_code.tools.not_stage_completed_6044.tool import NotStageCompleted6044ToolConfig
from workflow_config_code.tools.not_stage_completed_discuss_prototype_0000.tool import \
    NotStageCompletedDiscussPrototype0000ToolConfig
from workflow_config_code.tools.run_compilation_h8i9.tool import RunCompilationH8i9ToolConfig
from workflow_config_code.agents.process_compilation_results_i9j0.agent import ProcessCompilationResultsI9j0AgentConfig
from workflow_config_code.messages.notify_compilation_started_h8i9.message import \
    NotifyCompilationStartedH8i9MessageConfig
from workflow_config_code.messages.notify_project_compiled_f5g6.message import NotifyProjectCompiledF5g6MessageConfig
from workflow_config_code.tools.save_env_file_d2aa.tool import SaveEnvFileD2aaToolConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "functional_requirements_to_prototype_java",
        "desc": "Complete workflow to transform functional requirements into a working application",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "functional_requirements_to_prototype_java"
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "start_save_functional_requirements",
                        "next": "save_functional_requirements",
                        "manual": False
                    }
                ]
            },
            "save_functional_requirements": {
                "transitions": [
                    {
                        "name": "functional_requirements_saved",
                        "next": "notify_saved_requirements",
                        "manual": False,
                        "processors": [
                            {
                                "name": SaveFunctionalRequirementsF2a1AgentConfig.get_name(),
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
            "notify_saved_requirements": {
                "transitions": [
                    {
                        "name": "proceed_to_generate_orchestrators",
                        "next": "generate_controller",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifySavedFunReqA1b2MessageConfig.get_name(),
                                "executionMode": "SYNC",
                                "config": {
                                    "calculationNodesTags": "ai_assistant"
                                }
                            }
                        ]
                    }
                ]
            },
            "generate_controller": {
                "transitions": [
                    {
                        "name": "controller_generated",
                        "next": "notify_controller_generated",
                        "manual": False,
                        "processors": [
                            {
                                "name": GenerateControllerD4e3AgentConfig.get_name(),
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
            "notify_controller_generated": {
                "transitions": [
                    {
                        "name": "proceed_to_generate_processors",
                        "next": "generate_processors_and_criteria",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyControllerGeneratedD3e4MessageConfig.get_name(),
                                "executionMode": "SYNC",
                                "config": {
                                    "calculationNodesTags": "ai_assistant"
                                }
                            }
                        ]
                    }
                ]
            },
            "generate_processors_and_criteria": {
                "transitions": [
                    {
                        "name": "processors_and_criteria_generated",
                        "next": "notify_processors_generated",
                        "manual": False,
                        "processors": [
                            {
                                "name": GenerateProcessorsAndCriteriaE5f4AgentConfig.get_name(),
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
            "notify_processors_generated": {
                "transitions": [
                    {
                        "name": "proceed_to_enhance_processors",
                        "next": "enhance_processors",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyProcessorsGeneratedE4f5MessageConfig.get_name(),
                                "executionMode": "SYNC",
                                "config": {
                                    "calculationNodesTags": "ai_assistant"
                                }
                            }
                        ]
                    }
                ]
            },
            "enhance_processors": {
                "transitions": [
                    {
                        "name": "processors_enhanced",
                        "next": "implement_business_logic",
                        "manual": False,
                        "processors": [
                            {
                                "name": EnhanceProcessorsG6h7AgentConfig.get_name(),
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
            "implement_business_logic": {
                "transitions": [
                    {
                        "name": "implement_business_logic",
                        "next": "generate_tests_for_processors",
                        "manual": False,
                        "processors": [
                            {
                                "name": ImplementProcessorsBusinessLogicG6h7AgentConfig.get_name(),
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
            "generate_tests_for_processors": {
                "transitions": [
                    {
                        "name": "generate_tests_for_processors",
                        "next": "notify_processors_enhanced",
                        "manual": False,
                        "processors": [
                            {
                                "name": GenerateTestsForProcessorsAgentConfig.get_name(),
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
            "notify_processors_enhanced": {
                "transitions": [
                    {
                        "name": "proceed_to_run_compilation",
                        "next": "run_compilation",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyProcessorsEnhancedG7h8MessageConfig.get_name(),
                                "executionMode": "SYNC",
                                "config": {
                                    "calculationNodesTags": "ai_assistant"
                                }
                            }
                        ]
                    }
                ]
            },
            "run_compilation": {
                "transitions": [
                    {
                        "name": "compilation_started",
                        "next": "notify_prototype_compiled",
                        "manual": False,
                        "processors": [
                            {
                                "name": CompileProjectF6g5AgentConfig.get_name(),
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
            "notify_prototype_compiled": {
                "transitions": [
                    {
                        "name": "workflow_completed",
                        "next": "waiting_prototype_discussion_requested",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyProjectCompiledF5g6MessageConfig.get_name(),
                                "executionMode": "SYNC",
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
                                "name": ProcessPrototypeDiscussion0000AgentConfig.get_name(),
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
                                "name": NotStageCompletedDiscussPrototype0000ToolConfig.get_name(),
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
                                "name": IsStageCompletedDiscussPrototype0000ToolConfig.get_name(),
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
                        "next": "migration_confirmation_requested",
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
            "migration_confirmation_requested": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "migration_confirmation_requested_submitted_answer",
                        "manual": True
                    },
                    {
                        "name": "manual_approve",
                        "next": "save_env_file",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "migration_confirmation_requested_submitted_answer",
                        "manual": True
                    }
                ]
            },
            "migration_confirmation_requested_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "migration_confirmation_requested_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessUserInput2185AgentConfig.get_name(),
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
            "migration_confirmation_requested_processing": {
                "transitions": [
                    {
                        "name": "process_migration_confirmation_processing",
                        "next": "migration_confirmation_requested",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": NotStageCompleted6044ToolConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000
                                }
                            }
                        }
                    },
                    {
                        "name": "process_migration_confirmation_success",
                        "next": "save_env_file",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsStageCompletedC00aToolConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000
                                }
                            }
                        }
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
                                "name": SaveEnvFileD2aaToolConfig.get_name(),
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
                                "name": DeleteFiles6818ToolConfig.get_name(),
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
                                "name": InitSetupWorkflow5f06ToolConfig.get_name(),
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
