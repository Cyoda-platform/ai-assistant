"""
DeployUserAppWorkflowConfig Configuration

Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.messages.message_deployment_rollback_c4f9.message import MessageDeploymentRollbackC4f9MessageConfig
from workflow_config_code.workflows.functions.lock_chat_670c.function import LockChat670cFunctionConfig
from workflow_config_code.workflows.messages.message_deployment_success_7458.message import MessageDeploymentSuccess7458MessageConfig
from workflow_config_code.workflows.functions.schedule_deploy_user_app_a3b7.function import ScheduleDeployUserAppA3b7FunctionConfig
from workflow_config_code.workflows.messages.message_deployment_failure_b556.message import MessageDeploymentFailureB556MessageConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "deploy_user_app",
        "desc": "Workflow for deploying user application",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
                "type": "simple",
                "jsonPath": "$.workflow_name",
                "operation": "EQUALS",
                "value": "deploy_user_app"
        },
        "states": {
                "initial_state": {
                        "transitions": [
                                {
                                        "name": "schedule_deploy_user_app",
                                        "next": "scheduled_deploy_user_app",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": ScheduleDeployUserAppA3b7FunctionConfig.get_name(),
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
                "scheduled_deploy_user_app": {
                        "transitions": [
                                {
                                        "name": "lock_chat",
                                        "next": "locked_chat_while_deployment",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": LockChat670cFunctionConfig.get_name(),
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
                                        "next": "deployed_app",
                                        "manual": True,
                                        "processors": [
                                                {
                                                        "name": MessageDeploymentSuccess7458MessageConfig.get_name(),
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
                                        "next": "deployed_app",
                                        "manual": True,
                                        "processors": [
                                                {
                                                        "name": MessageDeploymentFailureB556MessageConfig.get_name(),
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
                                        "next": "deployed_app",
                                        "manual": True,
                                        "processors": [
                                                {
                                                        "name": MessageDeploymentRollbackC4f9MessageConfig.get_name(),
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
                "deployed_app": {
                        "transitions": [
                                {
                                        "name": "lock_chat",
                                        "next": "locked_chat",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": LockChat670cFunctionConfig.get_name(),
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
                                        "next": "deployed_app",
                                        "manual": True
                                }
                        ]
                }
        }
}

