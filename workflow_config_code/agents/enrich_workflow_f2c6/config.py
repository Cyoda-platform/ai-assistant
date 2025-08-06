"""
EnrichWorkflowF2c6AgentConfig Configuration

Generated from config: workflow_configs/agents/enrich_workflow_f2c6/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.prompts.enrich_workflow_9e00.prompt import EnrichWorkflow9e00PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "model": {},
        "memory_tags": [
                "workflow_generation"
        ],
        "messages": [
                {
                        "role": "user",
                        "content_from_file": EnrichWorkflow9e00PromptConfig.get_name()
                }
        ],
        "response_format": {
                "name": "workflow_design_schema",
                "description": "workflow design schema",
                "schema": {
                        "type": "object",
                        "required": [
                                "version",
                                "name",
                                "initialState",
                                "states"
                        ],
                        "properties": {
                                "version": {
                                        "type": "string"
                                },
                                "name": {
                                        "type": "string"
                                },
                                "desc": {
                                        "type": "string"
                                },
                                "initialState": {
                                        "type": "string",
                                        "enum": [
                                                "none"
                                        ]
                                },
                                "active": {
                                        "type": "boolean"
                                },
                                "states": {
                                        "type": "object",
                                        "additionalProperties": {
                                                "type": "object",
                                                "required": [
                                                        "transitions"
                                                ],
                                                "properties": {
                                                        "transitions": {
                                                                "type": "array",
                                                                "items": {
                                                                        "type": "object",
                                                                        "required": [
                                                                                "name",
                                                                                "next",
                                                                                "manual"
                                                                        ],
                                                                        "properties": {
                                                                                "name": {
                                                                                        "type": "string"
                                                                                },
                                                                                "next": {
                                                                                        "type": "string"
                                                                                },
                                                                                "manual": {
                                                                                        "type": "boolean",
                                                                                        "enum": [
                                                                                                False
                                                                                        ]
                                                                                },
                                                                                "processors": {
                                                                                        "type": "array",
                                                                                        "items": {
                                                                                                "type": "object",
                                                                                                "required": [
                                                                                                        "name",
                                                                                                        "config"
                                                                                                ],
                                                                                                "properties": {
                                                                                                        "name": {
                                                                                                                "type": "string"
                                                                                                        },
                                                                                                        "executionMode": {
                                                                                                                "type": "string",
                                                                                                                "enum": [
                                                                                                                        "SYNC",
                                                                                                                        "ASYNC_NEW_TX",
                                                                                                                        "ASYNC_SAME_TX"
                                                                                                                ]
                                                                                                        },
                                                                                                        "config": {
                                                                                                                "type": "object",
                                                                                                                "required": [
                                                                                                                        "calculationNodesTags"
                                                                                                                ],
                                                                                                                "properties": {
                                                                                                                        "attachEntity": {
                                                                                                                                "type": "boolean"
                                                                                                                        },
                                                                                                                        "calculationNodesTags": {
                                                                                                                                "type": "string",
                                                                                                                                "enum": [
                                                                                                                                        "cyoda_application"
                                                                                                                                ]
                                                                                                                        },
                                                                                                                        "responseTimeoutMs": {
                                                                                                                                "type": "integer"
                                                                                                                        },
                                                                                                                        "retryPolicy": {
                                                                                                                                "type": "string",
                                                                                                                                "enum": [
                                                                                                                                        "FIXED",
                                                                                                                                        "EXPONENTIAL",
                                                                                                                                        "LINEAR"
                                                                                                                                ]
                                                                                                                        }
                                                                                                                }
                                                                                                        }
                                                                                                }
                                                                                        }
                                                                                },
                                                                                "criterion": {
                                                                                        "type": "object",
                                                                                        "required": [
                                                                                                "type"
                                                                                        ],
                                                                                        "properties": {
                                                                                                "type": {
                                                                                                        "type": "string",
                                                                                                        "enum": [
                                                                                                                "function",
                                                                                                                "group",
                                                                                                                "simple"
                                                                                                        ]
                                                                                                },
                                                                                                "function": {
                                                                                                        "type": "object",
                                                                                                        "required": [
                                                                                                                "name",
                                                                                                                "config"
                                                                                                        ],
                                                                                                        "properties": {
                                                                                                                "name": {
                                                                                                                        "type": "string"
                                                                                                                },
                                                                                                                "config": {
                                                                                                                        "type": "object",
                                                                                                                        "required": [
                                                                                                                                "calculationNodesTags"
                                                                                                                        ],
                                                                                                                        "properties": {
                                                                                                                                "attachEntity": {
                                                                                                                                        "type": "boolean"
                                                                                                                                },
                                                                                                                                "calculationNodesTags": {
                                                                                                                                        "type": "string",
                                                                                                                                        "enum": [
                                                                                                                                                "cyoda_application"
                                                                                                                                        ]
                                                                                                                                },
                                                                                                                                "responseTimeoutMs": {
                                                                                                                                        "type": "integer"
                                                                                                                                },
                                                                                                                                "retryPolicy": {
                                                                                                                                        "type": "string",
                                                                                                                                        "enum": [
                                                                                                                                                "FIXED",
                                                                                                                                                "EXPONENTIAL",
                                                                                                                                                "LINEAR"
                                                                                                                                        ]
                                                                                                                                }
                                                                                                                        }
                                                                                                                },
                                                                                                                "criterion": {
                                                                                                                        "type": "object",
                                                                                                                        "properties": {
                                                                                                                                "type": {
                                                                                                                                        "type": "string",
                                                                                                                                        "enum": [
                                                                                                                                                "simple",
                                                                                                                                                "group"
                                                                                                                                        ]
                                                                                                                                },
                                                                                                                                "jsonPath": {
                                                                                                                                        "type": "string"
                                                                                                                                },
                                                                                                                                "operation": {
                                                                                                                                        "type": "string",
                                                                                                                                        "enum": [
                                                                                                                                                "EQUALS",
                                                                                                                                                "GREATER_THAN",
                                                                                                                                                "GREATER_OR_EQUAL",
                                                                                                                                                "LESS_THAN",
                                                                                                                                                "LESS_OR_EQUAL",
                                                                                                                                                "NOT_EQUALS"
                                                                                                                                        ]
                                                                                                                                },
                                                                                                                                "value": {
                                                                                                                                        "oneOf": [
                                                                                                                                                {
                                                                                                                                                        "type": "string"
                                                                                                                                                },
                                                                                                                                                {
                                                                                                                                                        "type": "number"
                                                                                                                                                },
                                                                                                                                                {
                                                                                                                                                        "type": "boolean"
                                                                                                                                                }
                                                                                                                                        ]
                                                                                                                                }
                                                                                                                        }
                                                                                                                }
                                                                                                        }
                                                                                                },
                                                                                                "jsonPath": {
                                                                                                        "type": "string"
                                                                                                },
                                                                                                "operation": {
                                                                                                        "type": "string",
                                                                                                        "enum": [
                                                                                                                "EQUALS",
                                                                                                                "GREATER_THAN",
                                                                                                                "GREATER_OR_EQUAL",
                                                                                                                "LESS_THAN",
                                                                                                                "LESS_OR_EQUAL",
                                                                                                                "NOT_EQUALS"
                                                                                                        ]
                                                                                                },
                                                                                                "value": {
                                                                                                        "oneOf": [
                                                                                                                {
                                                                                                                        "type": "string"
                                                                                                                },
                                                                                                                {
                                                                                                                        "type": "number"
                                                                                                                },
                                                                                                                {
                                                                                                                        "type": "boolean"
                                                                                                                }
                                                                                                        ]
                                                                                                },
                                                                                                "operator": {
                                                                                                        "type": "string",
                                                                                                        "enum": [
                                                                                                                "AND",
                                                                                                                "OR"
                                                                                                        ]
                                                                                                },
                                                                                                "conditions": {
                                                                                                        "type": "array",
                                                                                                        "items": {
                                                                                                                "type": "object",
                                                                                                                "required": [
                                                                                                                        "type",
                                                                                                                        "jsonPath",
                                                                                                                        "operation",
                                                                                                                        "value"
                                                                                                                ],
                                                                                                                "properties": {
                                                                                                                        "type": {
                                                                                                                                "type": "string",
                                                                                                                                "enum": [
                                                                                                                                        "simple"
                                                                                                                                ]
                                                                                                                        },
                                                                                                                        "jsonPath": {
                                                                                                                                "type": "string"
                                                                                                                        },
                                                                                                                        "operation": {
                                                                                                                                "type": "string",
                                                                                                                                "enum": [
                                                                                                                                        "EQUALS",
                                                                                                                                        "GREATER_THAN",
                                                                                                                                        "GREATER_OR_EQUAL",
                                                                                                                                        "LESS_THAN",
                                                                                                                                        "LESS_OR_EQUAL",
                                                                                                                                        "NOT_EQUALS"
                                                                                                                                ]
                                                                                                                        },
                                                                                                                        "value": {
                                                                                                                                "oneOf": [
                                                                                                                                        {
                                                                                                                                                "type": "string"
                                                                                                                                        },
                                                                                                                                        {
                                                                                                                                                "type": "number"
                                                                                                                                        },
                                                                                                                                        {
                                                                                                                                                "type": "boolean"
                                                                                                                                        }
                                                                                                                                ]
                                                                                                                        }
                                                                                                                }
                                                                                                        }
                                                                                                }
                                                                                        }
                                                                                }
                                                                        }
                                                                }
                                                        }
                                                }
                                        }
                                }
                        }
                }
        },
        "input": {
                "local_fs": [
                        "src/main/java/com/java_template/application/workflow/{EntityName}.json"
                ]
        },
        "output": {
                "local_fs": [
                        "src/main/java/com/java_template/application/workflow/{EntityName}.json"
                ]
        },
        "publish": False
}
