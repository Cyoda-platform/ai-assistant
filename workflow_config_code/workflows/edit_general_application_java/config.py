"""
FunctionalRequirementsToPrototypeJavaWorkflowConfig Configuration

Configuration data for the functional requirements to application workflow.
"""

from typing import Any, Dict, Callable

from workflow_config_code.agents.process_user_input_2185.agent import ProcessUserInput2185AgentConfig
from workflow_config_code.messages.notify_editing_started.message import NotifyEditingStartedMessageConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "edit_general_application_java",
        "desc": "Complete workflow to transform functional requirements into a working application",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "edit_general_application_java"
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "start_edit_application",
                        "next": "edit_application_requested",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyEditingStartedMessageConfig.get_name(),
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
            "processing_user_input": {
                "transitions": [
                    {
                        "name": "submit_answer",
                        "next": "edit_application_requested",
                        "manual": True
                    },
                    {
                        "name": "rollback",
                        "next": "edit_application_requested",
                        "manual": True
                    },
                    {
                        "name": "manual_approve",
                        "next": "edit_application_requested",
                        "manual": True
                    }
                ]
            },
            "edit_application_requested": {
                "transitions": [
                    {
                        "name": "edit_application_requested_processing",
                        "next": "processing_user_input",
                        "manual": False,
                        "processors": [
                            {
                                "name": NotifyEditingStartedMessageConfig.get_name(),
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000
                                }
                            },
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
        }
    }
