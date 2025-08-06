"""
GeneratingGenAppWorkflowJavaWorkflowConfig Configuration

Generated from config: workflow_configs/workflows/generating_gen_app_workflow_java.json
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
from workflow_config_code.agents.analyze_workflows_and_extract_operations_960f.agent import AnalyzeWorkflowsAndExtractOperations960fAgentConfig
from workflow_config_code.agents.design_workflow_config_from_code_fe21.agent import DesignWorkflowConfigFromCodeFe21AgentConfig
from workflow_config_code.agents.generate_criteria_from_workflows_42a6.agent import GenerateCriteriaFromWorkflows42a6AgentConfig
from workflow_config_code.tools.convert_workflow_to_dto_d870.tool import ConvertWorkflowToDtoD870ToolConfig
from workflow_config_code.agents.enrich_workflow_f2c6.agent import EnrichWorkflowF2c6AgentConfig
from workflow_config_code.agents.save_workflow_code_977a.agent import SaveWorkflowCode977aAgentConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {
        "version": "1.0",
        "name": "generating_gen_app_workflow_java",
        "desc": "Migrated from generating_gen_app_workflow_java",
        "initialState": "none",
        "active": True,
        "criterion": {
                "type": "simple",
                "jsonPath": "$.workflow_name",
                "operation": "EQUALS",
                "value": "generating_gen_app_workflow_java"
        },
        "states": {
                "none": {
                        "transitions": [
                                {
                                        "name": "start_workflow_generation",
                                        "next": "started_workflow_generation",
                                        "manual": False
                                }
                        ]
                },
                "started_workflow_generation": {
                        "transitions": [
                                {
                                        "name": "save_workflow_code",
                                        "next": "saved_workflow_code",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": SaveWorkflowCode977aAgentConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant"
                                                        }
                                                }
                                        ]
                                }
                        ]
                },
                "saved_workflow_code": {
                        "transitions": [
                                {
                                        "name": "design_workflow_config_from_code",
                                        "next": "designed_workflow_json",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": DesignWorkflowConfigFromCodeFe21AgentConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant"
                                                        }
                                                }
                                        ]
                                }
                        ]
                },
                "designed_workflow_json": {
                        "transitions": [
                                {
                                        "name": "enrich_workflow",
                                        "next": "formatted_workflow_json",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": EnrichWorkflowF2c6AgentConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant"
                                                        }
                                                }
                                        ]
                                }
                        ]
                },
                "formatted_workflow_json": {
                        "transitions": [
                                {
                                        "name": "convert_workflow_to_cyoda_dto",
                                        "next": "converted_workflow_to_cyoda_dto",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": ConvertWorkflowToDtoD870ToolConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant"
                                                        }
                                                }
                                        ]
                                }
                        ]
                },
                "converted_workflow_to_cyoda_dto": {
                        "transitions": [
                                {
                                        "name": "analyze_workflows_and_extract_operations",
                                        "next": "processors_generated",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": AnalyzeWorkflowsAndExtractOperations960fAgentConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant"
                                                        }
                                                }
                                        ]
                                }
                        ]
                },
                "processors_generated": {
                        "transitions": [
                                {
                                        "name": "generate_criteria_from_workflows",
                                        "next": "criteria_generated",
                                        "manual": False,
                                        "processors": [
                                                {
                                                        "name": GenerateCriteriaFromWorkflows42a6AgentConfig.get_name(),
                                                        "executionMode": "ASYNC_NEW_TX",
                                                        "config": {
                                                                "calculationNodesTags": "ai_assistant"
                                                        }
                                                }
                                        ]
                                }
                        ]
                },
                "criteria_generated": {
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
