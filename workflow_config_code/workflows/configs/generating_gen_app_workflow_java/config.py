"""
GeneratingGenAppWorkflowJavaWorkflowConfig Configuration

Generated from config: workflow_configs/configs/generating_gen_app_workflow_java.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.workflows.agents.configs.enrich_workflow_f2c6.agent import EnrichWorkflowF2c6AgentConfig
from workflow_config_code.workflows.functions.convert_workflow_to_dto_d870.function import ConvertWorkflowToDtoD870FunctionConfig
from workflow_config_code.workflows.agents.configs.analyze_workflows_and_extract_operations_960f.agent import AnalyzeWorkflowsAndExtractOperations960fAgentConfig
from workflow_config_code.workflows.agents.configs.generate_criteria_from_workflows_42a6.agent import GenerateCriteriaFromWorkflows42a6AgentConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "generating_gen_app_workflow_java",
        "desc": "Migrated from generating_gen_app_workflow_java",
        "initialState": "initial_state",
        "active": True,
        "criterion": {
            "type": "simple",
            "jsonPath": "$.workflow_name",
            "operation": "EQUALS",
            "value": "generating_gen_app_workflow_java",
        },
        "states": {
            "initial_state": {
                "transitions": [
                    {
                        "name": "start_workflow_generation",
                        "next": "started_workflow_generation",
                        "manual": False,
                    },
                    {
                        "name": "retry",
                        "next": "initial_state",
                        "manual": True,
                    },
                    {
                        "name": "fail_initial_state",
                        "next": "locked_initial_state",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_initial_state": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "initial_state",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_initial_state",
                        "next": "locked_locked_initial_state",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_initial_state": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_initial_state",
                        "next": "locked_locked_locked_initial_state",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_initial_state": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_initial_state",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_initial_state",
                        "next": "locked_locked_locked_locked_initial_state",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_initial_state": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_initial_state",
                        "manual": True,
                    },
                ],
            },
            "started_workflow_generation": {
                "transitions": [
                    {
                        "name": "enrich_workflow",
                        "next": "formatted_workflow_json",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.enrich_workflow_f2c6",
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        ],
                    },
                    {
                        "name": "retry",
                        "next": "started_workflow_generation",
                        "manual": True,
                    },
                    {
                        "name": "fail_started_workflow_generation",
                        "next": "locked_started_workflow_generation",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_started_workflow_generation": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "started_workflow_generation",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_started_workflow_generation",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_started_workflow_generation",
                        "next": "locked_locked_started_workflow_generation",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_started_workflow_generation": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_started_workflow_generation",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_started_workflow_generation",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_started_workflow_generation",
                        "next": "locked_locked_locked_started_workflow_generation",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_started_workflow_generation": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_started_workflow_generation",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_started_workflow_generation",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_started_workflow_generation",
                        "next": "locked_locked_locked_locked_started_workflow_generation",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_started_workflow_generation": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_started_workflow_generation",
                        "manual": True,
                    },
                ],
            },
            "formatted_workflow_json": {
                "transitions": [
                    {
                        "name": "convert_workflow_to_cyoda_dto",
                        "next": "converted_workflow_to_cyoda_dto",
                        "manual": False,
                        "processors": [
                            {
                                "name": "FunctionProcessor.convert_workflow_to_dto_d870",
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        ],
                    },
                    {
                        "name": "retry",
                        "next": "formatted_workflow_json",
                        "manual": True,
                    },
                    {
                        "name": "fail_formatted_workflow_json",
                        "next": "locked_formatted_workflow_json",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_formatted_workflow_json": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "formatted_workflow_json",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_formatted_workflow_json",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_formatted_workflow_json",
                        "next": "locked_locked_formatted_workflow_json",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_formatted_workflow_json": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_formatted_workflow_json",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_formatted_workflow_json",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_formatted_workflow_json",
                        "next": "locked_locked_locked_formatted_workflow_json",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_formatted_workflow_json": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_formatted_workflow_json",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_formatted_workflow_json",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_formatted_workflow_json",
                        "next": "locked_locked_locked_locked_formatted_workflow_json",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_formatted_workflow_json": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_formatted_workflow_json",
                        "manual": True,
                    },
                ],
            },
            "converted_workflow_to_cyoda_dto": {
                "transitions": [
                    {
                        "name": "analyze_workflows_and_extract_operations",
                        "next": "processors_generated",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.analyze_workflows_and_extract_operations_960f",
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        ],
                    },
                    {
                        "name": "retry",
                        "next": "converted_workflow_to_cyoda_dto",
                        "manual": True,
                    },
                    {
                        "name": "fail_converted_workflow_to_cyoda_dto",
                        "next": "locked_converted_workflow_to_cyoda_dto",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_converted_workflow_to_cyoda_dto": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "converted_workflow_to_cyoda_dto",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_converted_workflow_to_cyoda_dto",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_converted_workflow_to_cyoda_dto",
                        "next": "locked_locked_converted_workflow_to_cyoda_dto",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_converted_workflow_to_cyoda_dto": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_converted_workflow_to_cyoda_dto",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_converted_workflow_to_cyoda_dto",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_converted_workflow_to_cyoda_dto",
                        "next": "locked_locked_locked_converted_workflow_to_cyoda_dto",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_converted_workflow_to_cyoda_dto": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_converted_workflow_to_cyoda_dto",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_converted_workflow_to_cyoda_dto",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_converted_workflow_to_cyoda_dto",
                        "next": "locked_locked_locked_locked_converted_workflow_to_cyoda_dto",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_converted_workflow_to_cyoda_dto": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_converted_workflow_to_cyoda_dto",
                        "manual": True,
                    },
                ],
            },
            "processors_generated": {
                "transitions": [
                    {
                        "name": "generate_criteria_from_workflows",
                        "next": "criteria_generated",
                        "manual": False,
                        "processors": [
                            {
                                "name": "AgentProcessor.generate_criteria_from_workflows_42a6",
                                "executionMode": "ASYNC_NEW_TX",
                                "config": {
                                    "calculationNodesTags": "ai_assistant",
                                    "responseTimeoutMs": 300000,
                                },
                            },
                        ],
                    },
                    {
                        "name": "retry",
                        "next": "processors_generated",
                        "manual": True,
                    },
                    {
                        "name": "fail_processors_generated",
                        "next": "locked_processors_generated",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_processors_generated": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "processors_generated",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_processors_generated",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_processors_generated",
                        "next": "locked_locked_processors_generated",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_processors_generated": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_processors_generated",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_processors_generated",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_processors_generated",
                        "next": "locked_locked_locked_processors_generated",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_processors_generated": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_processors_generated",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_processors_generated",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_processors_generated",
                        "next": "locked_locked_locked_locked_processors_generated",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_processors_generated": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_processors_generated",
                        "manual": True,
                    },
                ],
            },
            "criteria_generated": {
                "transitions": [
                    {
                        "name": "lock_chat",
                        "next": "locked_chat",
                        "manual": False,
                    },
                    {
                        "name": "retry",
                        "next": "criteria_generated",
                        "manual": True,
                    },
                    {
                        "name": "fail_criteria_generated",
                        "next": "locked_criteria_generated",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_criteria_generated": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "criteria_generated",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_criteria_generated",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_criteria_generated",
                        "next": "locked_locked_criteria_generated",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_criteria_generated": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_criteria_generated",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_criteria_generated",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_criteria_generated",
                        "next": "locked_locked_locked_criteria_generated",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_criteria_generated": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_criteria_generated",
                        "manual": True,
                    },
                    {
                        "name": "retry",
                        "next": "locked_locked_locked_criteria_generated",
                        "manual": True,
                    },
                    {
                        "name": "fail_locked_locked_locked_criteria_generated",
                        "next": "locked_locked_locked_locked_criteria_generated",
                        "manual": False,
                        "criterion": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "type": "simple",
                                    "jsonPath": "$.failed",
                                    "operation": "EQUALS",
                                    "value": True,
                                },
                            ],
                        },
                    },
                ],
            },
            "locked_locked_locked_locked_criteria_generated": {
                "transitions": [
                    {
                        "name": "unlock",
                        "next": "locked_locked_locked_criteria_generated",
                        "manual": True,
                    },
                ],
            },
        },
    }
