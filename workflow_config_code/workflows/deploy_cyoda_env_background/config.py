"""
DeployCyodaEnvBackgroundWorkflowConfig Configuration

Generated from config: workflow_configs/workflows/deploy_cyoda_env_background.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.schedule_deploy_env_f9ed.tool import ScheduleDeployEnvF9edToolConfig
from workflow_config_code.tools.lock_chat_670c.tool import LockChat670cToolConfig
from workflow_config_code.messages.notify_deployment_success_7458.message import NotifyDeploymentSuccess7458MessageConfig
from workflow_config_code.messages.notify_deployment_failure_b556.message import NotifyDeploymentFailureB556MessageConfig
from workflow_config_code.messages.notify_deployment_rollback_c4f9.message import NotifyDeploymentRollbackC4f9MessageConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "deploy_cyoda_env_background",
        "desc": "Background workflow for deploying Cyoda environment",
        "initialState": "none",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "deploy_cyoda_env_background"
        },
        "states": {
            "none": {
                "transitions": [
                    {
                        "name": "schedule_deploy_env",
                        "next": "scheduled_deploy_env",
                        "manual": False,
                        "processors": [
                            {
                                "name": ScheduleDeployEnvF9edToolConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                    "publish": False,
                                    "memory_tags": ["chat_deploy_env", "general_memory_tag"]
                                }
                            }
                        ]
                    }
                ]
            },
            "scheduled_deploy_env": {
                "transitions": [
                    {
                        "name": "lock_chat",
                        "next": "locked_chat_while_deployment",
                        "manual": False,
                        "processors": [
                            {
                                "name": LockChat670cToolConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                    "publish": True
                                }
                            }
                        ]
                    }
                ]
            },
            "locked_chat_while_deployment": {
                "transitions": [
                    {
                        "name": "finish_deployment_success",
                        "next": "deployed_env",
                        "manual": True,
                        "processors": [
                            {
                                "name": NotifyDeploymentSuccess7458MessageConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    },
                    {
                        "name": "finish_deployment_failure",
                        "next": "deployed_env",
                        "manual": True,
                        "processors": [
                            {
                                "name": NotifyDeploymentFailureB556MessageConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            }
                        ]
                    },
                    {
                        "name": "rollback",
                        "next": "deployed_env",
                        "manual": True,
                        "processors": [
                            {
                                "name": NotifyDeploymentRollbackC4f9MessageConfig.get_name(),
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
            "deployed_env": {
                "transitions": [
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False,
                        "processors": [
                            {
                                "name": LockChat670cToolConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                    "publish": False
                                }
                            }
                        ]
                    }
                ]
            },
            "locked_chat": {
                "transitions": [
                    {
                        "name": "unlock_chat",
                        "next": "deployed_env",
                        "manual": True
                    }
                ]
            }
        }
    }
