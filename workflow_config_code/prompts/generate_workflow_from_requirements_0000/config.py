"""
GenerateWorkflowFromRequirements0000PromptConfig Configuration

Generated from config: workflow_configs/prompts/generate_workflow_from_requirements_0000/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: \
        """Get the list of entities with 'list_directory_files' tool.

For each entity:
1. Design a workflow based on the functional requirements. 
2. Call 'add_application_resource' with:
   - resource_path = 'src/main/resources/workflow/{entityName}/version_1/{EntityName}.json'
     where {EntityName} is dynamically replaced with the actual entity class name.
     replace entityName with the actual entity name in lower case. Replace {EntityName} with the actual entity name in CamelCase.
   - file_contents = workflow JSON.

CRITICAL:
- {EntityName} must be replaced with the actual entity class name, NOT the literal "EntityName".
- Do NOT create a workflow for "EntityName" placeholder.

Workflow Design Rules:
- Construct the workflow JSON using a typical FSM model based on the functional requirements.
- Avoid loops in the state transitions.
- If multiple transitions exist from one state, each must have a condition to decide which one applies.
- Limit processors to 1-2 unless the user explicitly requests more. At least one processor is recommended per workflow.
- JSON should be an ordered dictionary of states.
- Each state has a list of transitions.
- Each transition must have:
  - name
  - next
  - manual = false (default is false, unless true is explicitly requested)
- A transition may include:
  - processors (list of processor definitions)
  - criterion (definition for conditional transitions)
Processors represent business logic execution (e.g. validation, data processing, data enrichment, data transformation, external API calls or business domain logic: order, approve, sign, notify), and criteria represent conditional logic.

Workflow JSON Example:
{
  "version": "1.0",
  "name": "{EntityName} Workflow",
  "desc": "Description of the workflow for {EntityName}",
  "initialState": "initial_state",
  "active": true,
  "states": {
    "initial_state": {
      "transitions": [
        {
          "name": "transition_to_01",
          "next": "state_01",
          "manual": false
        }
      ]
    },
    "state_01": {
      "transitions": [
        {
          "name": "transition_to_02",
          "next": "state_02",
          "manual": false,
          "processors": [
            {
              "name": "ProcessorClassName", -- CamelCase the processor class name
              "config": {
                "calculationNodesTags": "cyoda_application"
              }
            }
          ]
        }
      ]
    },
    "state_02": {
      "transitions": [
        {
          "name": "transition_with_criterion_simple",
          "next": "state_criterion_check_01",
          "manual": false,
          "criterion": {
            "type": "function",
            "function": {
              "name": "CriterionClassName", -- CamelCase the criterion class name
              "config": {
                "calculationNodesTags": "cyoda_application"
              }
            }
          }
        }
      ]
    }
  }
}

Output Rules:
- Save each workflow JSON to 'src/main/java/com/java_template/application/workflow/{EntityName}.json' using 'add_application_resource'.
- Generate valid JSON only. No extra text or markdown.
- Ensure no file named 'EntityName.json' is ever created unless there is literally an entity with that name.
- Avoid putting criterion and processors in the same transition if possible. Ideally, each transition has either a criterion or a processor, but not both.

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
}
"""

