"""
BuildGeneralApplicationJavaWorkflowConfig Configuration

Generated from config: workflow_configs/workflows/build_general_application_java.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable

from workflow_config_code.messages.notify_prototype_generation_0000.message import \
    NotifyPrototypeGeneration0000MessageConfig
from workflow_config_code.tools.generate_prototype_sketch_2269 import GeneratePrototypeSketch2269FunctionConfig
from workflow_config_code.messages.notify_workflows_extracted_0000.message import \
    NotifyWorkflowsExtracted0000MessageConfig
from workflow_config_code.tools.is_stage_completed_e7bf.tool import IsStageCompletedE7bfToolConfig
from workflow_config_code.tools.is_stage_completed_8a02.tool import IsStageCompleted8a02ToolConfig
from workflow_config_code.messages.welcome_user_25fc.message import WelcomeUser25fcMessageConfig
from workflow_config_code.agents.process_configs_discussion_0000.agent import ProcessConfigsDiscussion0000AgentConfig
from workflow_config_code.messages.notify_generated_original_requirements_b94e.message import \
    NotifyGeneratedOriginalRequirementsB94eMessageConfig
from workflow_config_code.messages.ask_about_api_d91f.message import AskAboutApiD91fMessageConfig
from workflow_config_code.agents.process_initial_question_cd33.agent import ProcessInitialQuestionCd33AgentConfig
from workflow_config_code.agents.generate_functional_requirements_accc.agent import \
    GenerateFunctionalRequirementsAcccAgentConfig
from workflow_config_code.agents.process_user_input_9a8e.agent import ProcessUserInput9a8eAgentConfig
from workflow_config_code.tools.init_chats_d512.tool import InitChatsD512ToolConfig
from workflow_config_code.tools.clone_repo_b60a.tool import CloneRepoB60aToolConfig
from workflow_config_code.agents.generate_workflow_from_requirements_0000.agent import \
    GenerateWorkflowFromRequirements0000AgentConfig
from workflow_config_code.messages.ask_about_api_063f.message import AskAboutApi063fMessageConfig
from workflow_config_code.tools.not_stage_completed_5e0e.tool import NotStageCompleted5e0eToolConfig
from workflow_config_code.tools.not_stage_completed_f259.tool import NotStageCompletedF259ToolConfig
from workflow_config_code.messages.notify_config_generation_0f5b.message import \
    NotifyConfigGeneration0f5bMessageConfig
from workflow_config_code.tools.is_stage_completed_b809.tool import IsStageCompletedB809ToolConfig
from workflow_config_code.messages.notify_generated_functional_requirements_0bee.message import \
    NotifyGeneratedFunctionalRequirements0beeMessageConfig
from workflow_config_code.agents.process_user_input_cd43.agent import ProcessUserInputCd43AgentConfig
from workflow_config_code.messages.notify_entities_extracted_ede4.message import \
    NotifyEntitiesExtractedEde4MessageConfig
from workflow_config_code.agents.extract_entities_from_prototype_22c6.agent import \
    ExtractEntitiesFromPrototype22c6AgentConfig
from workflow_config_code.agents.process_user_input_2c31.agent import ProcessUserInput2c31AgentConfig
from workflow_config_code.agents.notify_user_env_deployed_58e2.agent import NotifyUserEnvDeployed58e2AgentConfig
from workflow_config_code.agents.define_functional_requirements_8ee2.agent import \
    DefineFunctionalRequirements8ee2AgentConfig
from workflow_config_code.tools.not_stage_completed_discuss_configs_0000.tool import \
    NotStageCompletedDiscussConfigs0000ToolConfig
from workflow_config_code.tools.is_stage_completed_discuss_configs_0000.tool import \
    IsStageCompletedDiscussConfigs0000ToolConfig
from workflow_config_code.messages.ask_to_discuss_configs_0000.message import AskToDiscussConfigs0000MessageConfig
from workflow_config_code.tools.not_stage_completed_f57d.tool import NotStageCompletedF57dToolConfig
from workflow_config_code.agents.generate_original_requirements_c87e.agent import \
    GenerateOriginalRequirementsC87eAgentConfig


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
            "value": "build_general_application_java"
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
                        "next": "prototype_discussion_requested_submitted_answer",
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
                        "next": "start_environment_setup",
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
                        "next": "generated_initial_cyoda_prototype",
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
                        "name": "resume_gen_prototype_cyoda_workflow_json",
                        "next": "validated_controller",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "name": "resume_gen_prototype_cyoda_workflow_json_criteria",
                            "operator": "AND",
                            "parameters": [
                                {
                                    "jsonPath": "resume_transition",
                                    "operatorType": "IEQUALS",
                                    "value": "resume_gen_prototype_cyoda_workflow_json",
                                    "type": "simple"
                                }
                            ]
                        }
                    },
                    {
                        "name": "resume_gen_entities",
                        "next": "validated_controller",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "name": "resume_gen_entities_criteria",
                            "operator": "AND",
                            "parameters": [
                                {
                                    "jsonPath": "resume_transition",
                                    "operatorType": "IEQUALS",
                                    "value": "resume_gen_entities",
                                    "type": "simple"
                                }
                            ]
                        }
                    },
                    {
                        "name": "resume_post_app_build_steps",
                        "next": "finished_app_generation_flow",
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
                                "name": WelcomeUser25fcMessageConfig.get_name(),
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
                                    "responseTimeoutMs": 300000
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
                        "next": "chats_initialized",
                        "manual": False,
                        "processors": [
                            {
                                "name": InitChatsD512ToolConfig.get_name(),
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
            "chats_initialized": {
                "transitions": [
                    {
                        "name": "generate_original_requirements",
                        "next": "generated_original_requirements",
                        "manual": False,
                        "processors": [
                            {
                                "name": GenerateOriginalRequirementsC87eAgentConfig.get_name(),
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
            "generated_original_requirements": {
                "transitions": [
                    {
                        "name": "notify_generated_original_requirements",
                        "next": "notified_generated_original_requirements",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyGeneratedOriginalRequirementsB94eMessageConfig.get_name(),
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
            "notified_generated_original_requirements": {
                "transitions": [
                    {
                        "name": "process_initial_question",
                        "next": "app_requirements_requested",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessInitialQuestionCd33AgentConfig.get_name(),
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
                                "name": ProcessUserInput2c31AgentConfig.get_name(),
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
            "app_requirements_requested_processing": {
                "transitions": [
                    {
                        "name": "process_application_requirement_processing",
                        "next": "app_requirements_requested",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": NotStageCompletedF57dToolConfig.get_name(),
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
                                "name": IsStageCompletedE7bfToolConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    }
                ]
            },
            "app_requirements_finalized": {
                "transitions": [
                    {
                        "name": "ask_about_api",
                        "next": "proceeded_to_functional_requirements",
                        "manual": False,
                        "processors": [
                            {
                                "name": AskAboutApi063fMessageConfig.get_name(),
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
            "proceeded_to_functional_requirements": {
                "transitions": [
                    {
                        "name": "define_functional_requirements",
                        "next": "functional_requirements_specified",
                        "manual": False,
                        "processors": [
                            {
                                "name": DefineFunctionalRequirements8ee2AgentConfig.get_name(),
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
            "functional_requirements_specified": {
                "transitions": [
                    {
                        "name": "ask_about_api",
                        "next": "api_inquired",
                        "manual": False,
                        "processors": [
                            {
                                "name": AskAboutApiD91fMessageConfig.get_name(),
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
            "api_inquired": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "api_inquired_submitted_answer",
                        "manual": True
                    },
                    {
                        "name": "manual_approve",
                        "next": "env_deployment_started",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "api_inquired_submitted_answer",
                        "manual": True
                    }
                ]
            },
            "api_inquired_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "api_inquired_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessUserInputCd43AgentConfig.get_name(),
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
            "api_inquired_processing": {
                "transitions": [
                    {
                        "name": "process_api_inquiry_processing",
                        "next": "api_inquired",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": NotStageCompleted5e0eToolConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    },
                    {
                        "name": "process_api_inquiry_success",
                        "next": "env_deployment_started",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsStageCompleted8a02ToolConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
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
            "env_deployment_started": {
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
                                    "responseTimeoutMs": 300000
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
                                    "responseTimeoutMs": 300000
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
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    },
                    {
                        "name": "rollback",
                        "next": "start_environment_setup",
                        "manual": True
                    }
                ]
            },
            "deployed_cyoda_env": {
                "transitions": [
                    {
                        "name": "notify_user_env_deployed",
                        "next": "api_discussion_completed",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyUserEnvDeployed58e2AgentConfig.get_name(),
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
            "api_discussion_completed": {
                "transitions": [
                    {
                        "name": "notify_prototype_generation",
                        "next": "configs_generation_notified",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyConfigGeneration0f5bMessageConfig.get_name(),
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
            "configs_generation_notified": {
                "transitions": [
                    {
                        "name": "generate_functional_requirements",
                        "next": "generated_functional_requirements",
                        "manual": False,
                        "processors": [
                            {
                                "name": GenerateFunctionalRequirementsAcccAgentConfig.get_name(),
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
            "generated_functional_requirements": {
                "transitions": [
                    {
                        "name": "notify_generated_functional_requirements",
                        "next": "notified_generated_functional_requirements",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyGeneratedFunctionalRequirements0beeMessageConfig.get_name(),
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
            "notified_generated_functional_requirements": {
                "transitions": [
                    {
                        "name": "extract_entities_from_prototype",
                        "next": "entities_extracted",
                        "manual": False,
                        "processors": [
                            {
                                "name": ExtractEntitiesFromPrototype22c6AgentConfig.get_name(),
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
            "entities_extracted": {
                "transitions": [
                    {
                        "name": "notify_entities_extracted",
                        "next": "notified_entities_extracted",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyEntitiesExtractedEde4MessageConfig.get_name(),
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
            "notified_entities_extracted": {
                "transitions": [
                    {
                        "name": "generate_workflows",
                        "next": "generated_workflows",
                        "manual": False,
                        "processors": [
                            {
                                "name": GenerateWorkflowFromRequirements0000AgentConfig.get_name(),
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
            "generated_workflows": {
                "transitions": [
                    {
                        "name": "notify_generated_workflows",
                        "next": "notified_generated_workflows",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyWorkflowsExtracted0000MessageConfig.get_name(),
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
            "notified_generated_workflows": {
                "transitions": [
                    {
                        "name": "ask_to_discuss_configs",
                        "next": "configs_discussion_requested",
                        "manual": False,
                        "processors": [
                            {
                                "name": AskToDiscussConfigs0000MessageConfig.get_name(),
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
            "configs_discussion_requested": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "configs_discussion_requested_submitted_answer",
                        "manual": True
                    },
                    {
                        "name": "manual_approve",
                        "next": "configs_discussion_completed",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "configs_discussion_requested_submitted_answer",
                        "manual": True
                    }
                ]
            },
            "configs_discussion_requested_submitted_answer": {
                "transitions": [
                    {
                        "name": "process_user_input",
                        "next": "configs_discussion_requested_processing",
                        "manual": False,
                        "processors": [
                            {
                                "name": ProcessConfigsDiscussion0000AgentConfig.get_name(),
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
            "configs_discussion_requested_processing": {
                "transitions": [
                    {
                        "name": "process_configs_discussion_processing",
                        "next": "configs_discussion_requested",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": NotStageCompletedDiscussConfigs0000ToolConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    },
                    {
                        "name": "process_configs_discussion_success",
                        "next": "configs_discussion_completed",
                        "manual": False,
                        "criterion": {
                            "type": "function",
                            "function": {
                                "name": IsStageCompletedDiscussConfigs0000ToolConfig.get_name(),
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        }
                    }
                ]
            },
            "configs_discussion_completed": {
                "transitions": [
                    {
                        "name": "notify_prototype_generation_started",
                        "next": "prototype_generation_started",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyPrototypeGeneration0000MessageConfig.get_name(),
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

            "prototype_generation_started": {
                "transitions": [
                    {
                        "name": "generate_prototype",
                        "next": "completed",
                        "manual": False,
                        "processors": [
                            {
                                "name": GeneratePrototypeSketch2269FunctionConfig.get_name(),
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
