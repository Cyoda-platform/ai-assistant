"""
BuildGeneralApplicationJavaWorkflowConfig Configuration

Generated from config: workflow_configs/workflows/build_general_application_java.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable

from workflow_config_code.agents.generate_app_python.agent import GenerateAppPythonAgentConfig
from workflow_config_code.messages.notify_project_compiled_f5g6.message import NotifyProjectCompiledF5g6MessageConfig
from workflow_config_code.messages.notify_project_compiled_f5g6_py.message import \
    NotifyProjectCompiledF5g6PyMessageConfig
from workflow_config_code.messages.welcome_user_optimized.message import WelcomeUserOptimizedMessageConfig
from workflow_config_code.tools.delete_files_6818.tool import DeleteFiles6818ToolConfig
from workflow_config_code.tools.init_setup_workflow_5f06.tool import InitSetupWorkflow5f06ToolConfig
from workflow_config_code.agents.process_user_input_9a8e.agent import ProcessUserInput9a8eAgentConfig
from workflow_config_code.tools.init_chats_d512.tool import InitChatsD512ToolConfig
from workflow_config_code.tools.clone_repo_b60a.tool import CloneRepoB60aToolConfig
from workflow_config_code.tools.not_stage_completed_f259.tool import NotStageCompletedF259ToolConfig
from workflow_config_code.tools.is_stage_completed_b809.tool import IsStageCompletedB809ToolConfig
from workflow_config_code.agents.notify_user_env_deployed_58e2.agent import NotifyUserEnvDeployed58e2AgentConfig
from workflow_config_code.tools.save_env_file_d2aa.tool import SaveEnvFileD2aaToolConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "build_general_application_java_optimized",
        "desc": "Migrated from build_general_application_java",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "build_general_application_java_optimized"
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "initialize",
                        "next": "initialized",
                        "manual": False
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
                                "name": CloneRepoB60aToolConfig.get_name(),
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
            "repository_cloned": {
                "transitions": [
                    {
                        "name": "init_chats",
                        "next": "env_deployment_notified",
                        "manual": False,
                        "processors": [
                            {
                                "name": InitChatsD512ToolConfig.get_name(),
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
            "waiting_for_user_deployment_input": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "env_deployment_started",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "env_deployment_started",
                        "manual": True
                    }
                ]
            },
            "env_deployment_notified": {
                "transitions": [
                    {
                        "name": "process_user_input",
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
                                "name": NotStageCompletedF259ToolConfig.get_name(),
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
                                "name": IsStageCompletedB809ToolConfig.get_name(),
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
                        "next": "completed",
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
            "completed": {
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
