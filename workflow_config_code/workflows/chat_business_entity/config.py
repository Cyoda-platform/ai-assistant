"""
ChatBusinessEntityWorkflowConfig Configuration

Generated from config: workflow_configs/workflows/chat_business_entity.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable



def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "chat_business_entity",
        "desc": "Migrated from chat_business_entity",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
                "type": "simple",
                "jsonPath": "$.workflow_name",
                "operation": "EQUALS",
                "value": "chat_business_entity"
        },
        "states": {
                "initial_state": {
                        "transitions": [
                                {
                                        "name": "initialize_chat",
                                        "next": "initialized_chat",
                                        "manual": False
                                }
                        ]
                },
                "initialized_chat": {
                        "transitions": [
                                {
                                        "name": "update_transition",
                                        "next": "initialized_chat",
                                        "manual": True
                                },
                                {
                                        "name": "delete",
                                        "next": "deleted",
                                        "manual": True
                                }
                        ]
                }
        }
}
