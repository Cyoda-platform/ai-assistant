"""
DeployCyodaEnvWorkflowConfig Configuration

Generated from config: workflow_configs/workflows/deploy_cyoda_env.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.schedule_deploy_env_f9ed.tool import ScheduleDeployEnvF9edTool
from workflow_config_code.tools.lock_chat_670c.tool import LockChat670cTool


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "deploy_cyoda_env",
        "desc": "Workflow for deploying Cyoda environment",
        "initialState": "none",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "deploy_cyoda_env"
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
                                "name": ScheduleDeployEnvF9edTool.get_name(),
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
            "scheduled_deploy_env": {
                "transitions": [
                    {
                        "name": "lock_chat",
                        "next": "locked_chat_while_deployment",
                        "manual": False,
                        "processors": [
                            {
                                "name": LockChat670cTool.get_name(),
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
            "locked_chat_while_deployment": {
                "transitions": [
                    {
                        "name": "finish_deployment_success",
                        "next": "deployed_env",
                        "manual": True
                    },
                    {
                        "name": "finish_deployment_failure",
                        "next": "deployed_env",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "deployed_env",
                        "manual": True
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
                                "name": LockChat670cTool.get_name(),
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
