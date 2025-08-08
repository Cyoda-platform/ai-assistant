"""
FunctionalRequirementsToApplicationWorkflowConfig Configuration

Configuration data for the functional requirements to application workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.agents.save_functional_requirements_f2a1.agent import SaveFunctionalRequirementsF2a1AgentConfig
from workflow_config_code.messages.notify_saved_fun_req_a1b2.message import NotifySavedFunReqA1b2MessageConfig
from workflow_config_code.tools.generate_workflow_orchestrators_g7h8.tool import GenerateWorkflowOrchestratorsG7h8ToolConfig
from workflow_config_code.messages.notify_parsed_configs_c2d3.message import NotifyParsedConfigsC2d3MessageConfig
from workflow_config_code.agents.generate_controller_d4e3.agent import GenerateControllerD4e3AgentConfig
from workflow_config_code.messages.notify_controller_generated_d3e4.message import NotifyControllerGeneratedD3e4MessageConfig
from workflow_config_code.agents.generate_processors_and_criteria_e5f4.agent import GenerateProcessorsAndCriteriaE5f4AgentConfig
from workflow_config_code.messages.notify_processors_generated_e4f5.message import NotifyProcessorsGeneratedE4f5MessageConfig
from workflow_config_code.agents.compile_project_f6g5.agent import CompileProjectF6g5AgentConfig
from workflow_config_code.messages.notify_project_compiled_f5g6.message import NotifyProjectCompiledF5g6MessageConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "Functional Requirements to Application Workflow",
        "desc": "Complete workflow to transform functional requirements into a working application",
        "initialState": "initial_state",
        "active": True,
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
                                    "responseTimeoutMs": 300000
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
                        "next": "generate_workflow_orchestrators",
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
            "generate_workflow_orchestrators": {
                "transitions": [
                    {
                        "name": "workflow_orchestrators_generated",
                        "next": "notify_parsed_configs",
                        "manual": False,
                        "processors": [
                            {
                                "name": GenerateWorkflowOrchestratorsG7h8ToolConfig.get_name(),
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
            "notify_parsed_configs": {
                "transitions": [
                    {
                        "name": "proceed_to_generate_controller",
                        "next": "generate_controller",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyParsedConfigsC2d3MessageConfig.get_name(),
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
                                    "responseTimeoutMs": 300000
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
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    }
                ]
            },
            "notify_processors_generated": {
                "transitions": [
                    {
                        "name": "proceed_to_compile_project",
                        "next": "compile_project",
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
            "compile_project": {
                "transitions": [
                    {
                        "name": "project_compiled",
                        "next": "notify_project_compiled",
                        "manual": False,
                        "processors": [
                            {
                                "name": CompileProjectF6g5AgentConfig.get_name(),
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
            "notify_project_compiled": {
                "transitions": [
                    {
                        "name": "workflow_completed",
                        "next": "completed",
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
            "completed": {
                "transitions": []
            }
        }
    }
