"""
GenerateWorkflowFromRequirements0000AgentConfig Configuration

Generated from config: workflow_configs/agents/generate_workflow_from_requirements_0000/agent.json
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
from workflow_config_code.tools.add_application_resource_3d0b.tool import AddApplicationResource3d0bToolConfig
from workflow_config_code.tools.list_directory_files_1ab7.tool import ListDirectoryFiles1ab7ToolConfig
from workflow_config_code.prompts.generate_workflow_from_requirements_0000.prompt import \
    GenerateWorkflowFromRequirements0000PromptConfig


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {
        "type": "prompt",
        "name": "generate_workflow_from_requirements_0000",
        "model": {},
        "memory_tags": [
            "configs_generation"
        ],
        "messages": [
            {
                "role": "user",
                "content_from_file": GenerateWorkflowFromRequirements0000PromptConfig.get_name()
            }
        ],
        "tools": [
            {
                "name": AddApplicationResource3d0bToolConfig.get_tool_name()
            },
            {
                "name": ListDirectoryFiles1ab7ToolConfig.get_tool_name()
            }
        ],
        "input": {
            "local_fs": [
                "src/main/java/com/java_template/prototype/functional_requirement.md"
            ]
        },
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
                                                "type": "boolean"
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
        "publish": False
    }
