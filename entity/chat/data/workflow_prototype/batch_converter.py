import json
import re
import uuid

# Sample state diagram text

sample_json_dict = {

    "notification": {
        "current_state (please update, it's just a placeholder)": {
            "transitions": {
                "transition_name": {
                    "next": "next_state",
                    "action": {
                        "name": "process_event (always this action name)",
                        "config": {
                            "type": "notification",
                            "notification": "Generic notification message.",
                            "publish": True,
                            "allow_anonymous_users": True
                        }
                    }
                }}}},
    "question": {
        "current_state (please update, it's just a placeholder)": {
            "transitions": {
                "transition_name": {
                    "next": "next_state", "action": {
                        "name": "process_event (always this action name)",
                        "config": {
                            "type": "question",
                            "question": "Generic question prompt?",
                            "example_answers": [
                                "Example answer 1",
                                "Example answer 2"
                            ],
                            "publish": True,
                            "allow_anonymous_users": True
                        }
                    }}}}},
    "function": {

        "current_state (please update, it's just a placeholder)": {
            "transitions": {
                "transition_name": {
                    "next": "next_state",
                    "action": {
                        "name": "process_event (always this action name)",
                        "config": {
                            "type": "function",
                            "function": {
                                "name": "generic_function",
                                "description": "Executes a generic function task.",
                                "strict": True,
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "param1": {"type": "string"},
                                        "param2": {"type": "number"}
                                    },
                                    "required": ["param1"]
                                }
                            }
                        }
                    }}}}},
    "prompt": {

        "current_state (please update, it's just a placeholder)": {
            "transitions": {
                "transition_name": {
                    "next": "next_state",
                    "action": {
                        "name": "process_event (always this action name)",
                        "config": {
                            "type": "prompt",
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        "Generic prompt message text."
                                    ]
                                }
                            ],
                            "publish": True,
                            "allow_anonymous_users": True
                        }
                    }}}}},
    "agent": {
        "current_state (please update, it's just a placeholder)": {
            "transitions": {
                "transition_name": {
                    "next": "next_state",
                    "manual": True,
                    "action": {
                        "name": "process_event (always this action name)",
                        "config": {
                            "type": "agent",
                            "publish": True,
                            "allow_anonymous_users": True,
                            "model": {},
                            "tools": [
                                {
                                    "type": "function",
                                    "function": {
                                        "name": "generic_tool",
                                        "description": "Generic tool for agent processing.",
                                        "strict": True,
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "query": {"type": "string"}
                                            },
                                            "required": ["query"],
                                            "additionalProperties": False
                                        }
                                    }
                                }
                            ],
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        "Generic agent prompt message."
                                    ]
                                }
                            ],
                            "tool_choice": "auto",
                            "max_iteration": 10,
                            "approve": True
                        }
                    }}}}
    },
    "condition": {
        "current_state (please update, it's just a placeholder)": {
            "transitions": {
                "transition_name": {
                    "next": "next_state",
                    "condition": {
                        "config": {
                            "type": "function",
                            "function": {
                                "name": "is_stage_completed",
                                "description": "Verifies stage is complete",
                                "params": {
                                    "transition": "transition_name"
                                }
                            }
                        }
                    }
                }
            }}}
}
schema_json_dict = {
    "notification": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Notification Schema",
        "type": "object",
        "properties": {
            "current_state (please update, it's just a placeholder)": {
                "type": "object",
                "properties": {
                    "transitions": {
                        "type": "object",
                        "patternProperties": {
                            "^.*$": {
                                "type": "object",
                                "properties": {
                                    "next": {"type": "string"},
                                    "action": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "config": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {"const": "notification"},
                                                    "notification": {"type": "string"},
                                                    "publish": {"type": "boolean"},
                                                    "allow_anonymous_users": {"type": "boolean"}
                                                },
                                                "required": [
                                                    "type",
                                                    "notification",
                                                    "publish",
                                                    "allow_anonymous_users"
                                                ],
                                                "additionalProperties": False
                                            }
                                        },
                                        "required": ["name", "config"],
                                        "additionalProperties": False
                                    }
                                },
                                "required": ["next", "action"],
                                "additionalProperties": False
                            }
                        },
                        "minProperties": 1,
                        "additionalProperties": False
                    }
                },
                "required": ["transitions"],
                "additionalProperties": False
            }
        },
        "required": ["current_state (please update, it's just a placeholder)"],
        "additionalProperties": False
    },
    "question": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Question Schema",
        "type": "object",
        "properties": {
            "current_state (please update, it's just a placeholder)": {
                "type": "object",
                "properties": {
                    "transitions": {
                        "type": "object",
                        "patternProperties": {
                            "^.*$": {
                                "type": "object",
                                "properties": {
                                    "next": {"type": "string"},
                                    "action": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "config": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {"const": "question"},
                                                    "question": {"type": "string"},
                                                    "example_answers": {
                                                        "type": "array",
                                                        "items": {"type": "string"}
                                                    },
                                                    "publish": {"type": "boolean"},
                                                    "allow_anonymous_users": {"type": "boolean"}
                                                },
                                                "required": [
                                                    "type",
                                                    "question",
                                                    "example_answers",
                                                    "publish",
                                                    "allow_anonymous_users"
                                                ],
                                                "additionalProperties": False
                                            }
                                        },
                                        "required": ["name", "config"],
                                        "additionalProperties": False
                                    }
                                },
                                "required": ["next", "action"],
                                "additionalProperties": False
                            }
                        },
                        "minProperties": 1,
                        "additionalProperties": False
                    }
                },
                "required": ["transitions"],
                "additionalProperties": False
            }
        },
        "required": ["current_state (please update, it's just a placeholder)"],
        "additionalProperties": False
    },
    "function": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Function Schema",
        "type": "object",
        "properties": {
            "current_state (please update, it's just a placeholder)": {
                "type": "object",
                "properties": {
                    "transitions": {
                        "type": "object",
                        "patternProperties": {
                            "^.*$": {
                                "type": "object",
                                "properties": {
                                    "next": {"type": "string"},
                                    "action": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "config": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {"const": "function"},
                                                    "function": {
                                                        "type": "object",
                                                        "properties": {
                                                            "name": {"type": "string"},
                                                            "description": {"type": "string"},
                                                            "strict": {"type": "boolean"},
                                                            "parameters": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "type": {"const": "object"},
                                                                    "properties": {
                                                                        "type": "object",
                                                                        "properties": {
                                                                            "param1": {"type": "string"},
                                                                            "param2": {"type": "number"}
                                                                        },
                                                                        "required": ["param1"],
                                                                        "additionalProperties": True
                                                                    }
                                                                },
                                                                "required": ["type", "properties"],
                                                                "additionalProperties": True
                                                            }
                                                        },
                                                        "required": [
                                                            "name",
                                                            "description",
                                                            "strict",
                                                            "parameters"
                                                        ],
                                                        "additionalProperties": False
                                                    }
                                                },
                                                "required": ["type", "function"],
                                                "additionalProperties": False
                                            }
                                        },
                                        "required": ["name", "config"],
                                        "additionalProperties": False
                                    }
                                },
                                "required": ["next", "action"],
                                "additionalProperties": False
                            }
                        },
                        "minProperties": 1,
                        "additionalProperties": False
                    }
                },
                "required": ["transitions"],
                "additionalProperties": False
            }
        },
        "required": ["current_state (please update, it's just a placeholder)"],
        "additionalProperties": False
    },
    "prompt": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Prompt Schema",
        "type": "object",
        "properties": {
            "current_state (please update, it's just a placeholder)": {
                "type": "object",
                "properties": {
                    "transitions": {
                        "type": "object",
                        "patternProperties": {
                            "^.*$": {
                                "type": "object",
                                "properties": {
                                    "next": {"type": "string"},
                                    "action": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "config": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {"const": "prompt"},
                                                    "messages": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "role": {"type": "string"},
                                                                "content": {
                                                                    "type": "array",
                                                                    "items": {"type": "string"}
                                                                }
                                                            },
                                                            "required": ["role", "content"],
                                                            "additionalProperties": False
                                                        }
                                                    },
                                                    "publish": {"type": "boolean"},
                                                    "allow_anonymous_users": {"type": "boolean"}
                                                },
                                                "required": [
                                                    "type",
                                                    "messages",
                                                    "publish",
                                                    "allow_anonymous_users"
                                                ],
                                                "additionalProperties": False
                                            }
                                        },
                                        "required": ["name", "config"],
                                        "additionalProperties": False
                                    }
                                },
                                "required": ["next", "action"],
                                "additionalProperties": False
                            }
                        },
                        "minProperties": 1,
                        "additionalProperties": False
                    }
                },
                "required": ["transitions"],
                "additionalProperties": False
            }
        },
        "required": ["current_state (please update, it's just a placeholder)"],
        "additionalProperties": False
    },
    "agent": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Agent Schema",
        "type": "object",
        "properties": {
            "current_state (please update, it's just a placeholder)": {
                "type": "object",
                "properties": {
                    "transitions": {
                        "type": "object",
                        "patternProperties": {
                            "^.*$": {
                                "type": "object",
                                "properties": {
                                    "next": {"type": "string"},
                                    "manual": {"type": "boolean"},
                                    "action": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "config": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {"const": "agent"},
                                                    "publish": {"type": "boolean"},
                                                    "allow_anonymous_users": {"type": "boolean"},
                                                    "model": {"type": "object"},
                                                    "tools": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "type": {"type": "string"},
                                                                "function": {
                                                                    "type": "object",
                                                                    "properties": {
                                                                        "name": {"type": "string"},
                                                                        "description": {"type": "string"},
                                                                        "strict": {"type": "boolean"},
                                                                        "parameters": {
                                                                            "type": "object",
                                                                            "properties": {
                                                                                "type": {"const": "object"},
                                                                                "properties": {
                                                                                    "type": "object",
                                                                                    "properties": {
                                                                                        "query": {"type": "string"}
                                                                                    },
                                                                                    "required": ["query"],
                                                                                    "additionalProperties": True
                                                                                }
                                                                            },
                                                                            "required": ["type", "properties"],
                                                                            "additionalProperties": True
                                                                        }
                                                                    },
                                                                    "required": [
                                                                        "name",
                                                                        "description",
                                                                        "strict",
                                                                        "parameters"
                                                                    ],
                                                                    "additionalProperties": False
                                                                }
                                                            },
                                                            "required": ["type", "function"],
                                                            "additionalProperties": False
                                                        }
                                                    },
                                                    "messages": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "role": {"type": "string"},
                                                                "content": {
                                                                    "type": "array",
                                                                    "items": {"type": "string"}
                                                                }
                                                            },
                                                            "required": ["role", "content"],
                                                            "additionalProperties": False
                                                        }
                                                    },
                                                    "tool_choice": {"type": "string"},
                                                    "max_iteration": {"type": "integer"},
                                                    "approve": {"type": "boolean"}
                                                },
                                                "required": [
                                                    "type",
                                                    "publish",
                                                    "allow_anonymous_users",
                                                    "model",
                                                    "tools",
                                                    "messages",
                                                    "tool_choice",
                                                    "max_iteration",
                                                    "approve"
                                                ],
                                                "additionalProperties": False
                                            }
                                        },
                                        "required": ["name", "config"],
                                        "additionalProperties": False
                                    }
                                },
                                "required": ["next", "manual", "action"],
                                "additionalProperties": False
                            }
                        },
                        "minProperties": 1,
                        "additionalProperties": False
                    }
                },
                "required": ["transitions"],
                "additionalProperties": False
            }
        },
        "required": ["current_state (please update, it's just a placeholder)"],
        "additionalProperties": False
    }
}


def convert_state_diagram_to_jsonl_dataset(input_file_path, output_file_path):
    # todo not all have  config!!
    # Allowed transition types based on the golden sample
    allowed_types = {"notification", "question", "function", "prompt", "agent", "condition"}
    # Split the diagram into lines and filter out header/empty lines
    with open(input_file_path, "r", encoding="utf-8") as f:
        state_diagram = f.read()

    lines = [line.strip() for line in state_diagram.strip().splitlines()]

    jsonl_items = []
    counter = 1

    # Regular expression to capture the transition type after "/"
    type_pattern = re.compile(r"/\s*(\w+)", re.IGNORECASE)

    for line in lines:
        # Skip header lines
        if not line or line.startswith("stateDiagram") or line.startswith("direction"):
            continue

        # Extract the type from the line (e.g., notification, question, function, prompt, agent)
        match = type_pattern.search(line)
        if not match:
            continue

        line_type = match.group(1).lower()
        if line_type not in allowed_types:
            continue

        # Create a prompt based on the detected transition type
        prompt_text = (
            f"Convert the following state diagram line into JSON following the golden sample format for a '{line_type}' transition:\n{line} . Golden json example: {json.dumps(sample_json_dict.get(line_type))}"
        )

        # Build the batch request JSON object
        request_obj = {
            "custom_id": f"{counter}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system",
                     "content": "You are a helpful assistant that converts mermaid state diagram transition line into fsm json config. State diagram line is provided in the following format: current_state --> next_state : transition_name (manual - optional) /action_type [action_details] (update with real data). Use real values from the transition to fill in current state, next state, transition name and so on"},
                    {"role": "user", "content": prompt_text}
                ],
                "response_format": {
                    "type": "json_object"
                },
                "max_tokens": 5000
            }
        }

        jsonl_items.append(request_obj)
        counter += 1

    with open(output_file_path, "w") as outfile:
        for item in jsonl_items:
            outfile.write(json.dumps(item) + "\n")

    print(f"Generated {output_file_path} with {len(jsonl_items)} items.")

def main():
    convert_state_diagram_to_jsonl_dataset(input_file_path="workflow_agentic_1.md", output_file_path=f"state_diagram_batch_{uuid.uuid4()}.jsonl")

if __name__ == '__main__':
    main()
