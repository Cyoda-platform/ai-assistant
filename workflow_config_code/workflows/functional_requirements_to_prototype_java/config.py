"""
FunctionalRequirementsToPrototypeJavaWorkflowConfig Configuration

Configuration data for the functional requirements to application workflow.
"""

from typing import Any, Dict, Callable

from common.config import const
from workflow_config_code.agents.compile_project_f6g5.agent import CompileProjectF6g5AgentConfig
from workflow_config_code.agents.fix_compilation_errors_i1j2.agent import FixCompilationErrorsI1j2AgentConfig
from workflow_config_code.agents.process_prototype_discussion_0000.agent import \
    ProcessPrototypeDiscussion0000AgentConfig
from workflow_config_code.messages.ask_to_confirm_migration_208e.message import AskToConfirmMigration208eMessageConfig
from workflow_config_code.agents.generate_controller_d4e3.agent import GenerateControllerD4e3AgentConfig
from workflow_config_code.agents.enhance_processors_g6h7.agent import EnhanceProcessorsG6h7AgentConfig
from workflow_config_code.messages.notify_processors_enhanced_g7h8.message import \
    NotifyProcessorsEnhancedG7h8MessageConfig
from workflow_config_code.tools.delete_files_6818.tool import DeleteFiles6818ToolConfig
from workflow_config_code.tools.init_setup_workflow_5f06.tool import InitSetupWorkflow5f06ToolConfig
from workflow_config_code.tools.is_stage_completed_discuss_prototype_0000.tool import \
    IsStageCompletedDiscussPrototype0000ToolConfig
from workflow_config_code.tools.not_stage_completed_discuss_prototype_0000.tool import \
    NotStageCompletedDiscussPrototype0000ToolConfig
from workflow_config_code.tools.run_compilation_h8i9.tool import RunCompilationH8i9ToolConfig
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
                        "next": "generate_controller",
                        "manual": False
                    }
                ]
            },
            "generate_controller": {
                "transitions": [
                    {
                        "name": "controller_generated",
                        "next": "run_init_compilation",
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
            "run_init_compilation": {
                "transitions": [
                    {
                        "name": "compilation_started",
                        "next": "enhance_processors",
                        "manual": False,
                        "processors": [
                            {
                                "name": RunCompilationH8i9ToolConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 1500000
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
                        "next": "notify_processors_enhanced",
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
            "notify_processors_enhanced": {
                "transitions": [
                    {
                        "name": "proceed_to_run_compilation",
                        "next": "run_compilation",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyProcessorsEnhancedG7h8MessageConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
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
                        "next": "process_compilation",
                        "manual": False,
                        "processors": [
                            {
                                "name": RunCompilationH8i9ToolConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 1500000
                                }
                            }
                        ]
                    }
                ]
            },
            "process_compilation": {
                "transitions": [
                    {
                        "name": "compilation_started",
                        "next": "fix_compilation_errors",
                        "manual": False,
                        "processors": [
                            {
                                "name": CompileProjectF6g5AgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 1500000
                                }
                            }
                        ],
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": f"$.workflow_cache.{const.GITHUB_ACTION_COMPILED}",
                                    "operation": "IEQUALS",
                                    "value": "false"
                                }
                            ]
                        }
                    },
                    {
                        "name": "notify_prototype_compiled",
                        "next": "notify_prototype_compiled",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": f"$.workflow_cache.{const.GITHUB_ACTION_COMPILED}",
                                    "operation": "IEQUALS",
                                    "value": "true"
                                }
                            ]
                        }
                    }
                ]
            },
            "fix_compilation_errors": {
                "transitions": [
                    {
                        "name": "processors_enhanced",
                        "next": "notify_processors_enhanced_i2",
                        "manual": False,
                        "processors": [
                            {
                                "name": FixCompilationErrorsI1j2AgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000
                                }
                            }
                        ],
                    }
                ]
            },

            "notify_processors_enhanced_i2": {
                "transitions": [
                    {
                        "name": "proceed_to_run_compilation",
                        "next": "run_compilation_i2",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyProcessorsEnhancedG7h8MessageConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant"
                                }
                            }
                        ]
                    }
                ]
            },
            "run_compilation_i2": {
                "transitions": [
                    {
                        "name": "compilation_started",
                        "next": "process_compilation_i2",
                        "manual": False,
                        "processors": [
                            {
                                "name": RunCompilationH8i9ToolConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 1500000
                                }
                            }
                        ]
                    }
                ]
            },
            "process_compilation_i2": {
                "transitions": [
                    {
                        "name": "compilation_started",
                        "next": "fix_compilation_errors_i2",
                        "manual": False,
                        "processors": [
                            {
                                "name": CompileProjectF6g5AgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 1500000
                                }
                            }
                        ],
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": f"$.workflow_cache.{const.GITHUB_ACTION_COMPILED}",
                                    "operation": "IEQUALS",
                                    "value": "false"
                                }
                            ]
                        }
                    },
                    {
                        "name": "notify_prototype_compiled",
                        "next": "notify_prototype_compiled",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": f"$.workflow_cache.{const.GITHUB_ACTION_COMPILED}",
                                    "operation": "IEQUALS",
                                    "value": "true"
                                }
                            ]
                        }
                    }
                ]
            },
            "fix_compilation_errors_i2": {
                "transitions": [
                    {
                        "name": "processors_enhanced",
                        "next": "notify_processors_enhanced_i3",
                        "manual": False,
                        "processors": [
                            {
                                "name": FixCompilationErrorsI1j2AgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000
                                }
                            }
                        ],
                    }
                ]
            },

            "notify_processors_enhanced_i3": {
                "transitions": [
                    {
                        "name": "proceed_to_run_compilation",
                        "next": "run_compilation_i3",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyProcessorsEnhancedG7h8MessageConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant"
                                }
                            }
                        ]
                    }
                ]
            },
            "run_compilation_i3": {
                "transitions": [
                    {
                        "name": "compilation_started",
                        "next": "process_compilation_i3",
                        "manual": False,
                        "processors": [
                            {
                                "name": RunCompilationH8i9ToolConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 1500000
                                }
                            }
                        ]
                    }
                ]
            },
            "process_compilation_i3": {
                "transitions": [
                    {
                        "name": "compilation_started",
                        "next": "fix_compilation_errors_i3",
                        "manual": False,
                        "processors": [
                            {
                                "name": CompileProjectF6g5AgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 1500000
                                }
                            }
                        ],
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": f"$.workflow_cache.{const.GITHUB_ACTION_COMPILED}",
                                    "operation": "IEQUALS",
                                    "value": "false"
                                }
                            ]
                        }
                    },
                    {
                        "name": "notify_prototype_compiled",
                        "next": "notify_prototype_compiled",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": f"$.workflow_cache.{const.GITHUB_ACTION_COMPILED}",
                                    "operation": "IEQUALS",
                                    "value": "true"
                                }
                            ]
                        }
                    }
                ]
            },
            "fix_compilation_errors_i3": {
                "transitions": [
                    {
                        "name": "processors_enhanced",
                        "next": "notify_prototype_compiled",
                        "manual": False,
                        "processors": [
                            {
                                "name": FixCompilationErrorsI1j2AgentConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 900000
                                }
                            }
                        ],
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
