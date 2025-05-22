import re
import json


def convert_state_diagram(diagram):
    # Split the input diagram into lines
    lines = diagram.strip().split("\n")

    # Initialize required data structures
    state_machine = {
        "initial_state": None,
        "states": {}
    }
    current_state = None

    # Parse each line of the diagram
    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Parse the initial state line
        if line.startswith("[*] -->"):
            state_machine["initial_state"] = line.split(" --> ")[1].strip()
            current_state = state_machine["initial_state"]
            # Initialize state in the states dictionary
            state_machine["states"][current_state] = {"transitions": {}}
            continue

        # Parse the state transition lines
        match = re.match(r"(\w+) --> (\w+) : (\w+) / (\w+)", line)
        if match:
            from_state, to_state, event, action = match.groups()

            # If the from_state doesn't exist in the dictionary, create it
            if from_state not in state_machine["states"]:
                state_machine["states"][from_state] = {"transitions": {}}

            # Create the transition with the details in the JSON format
            state_machine["states"][from_state]["transitions"][event] = {
                "next": to_state,
                "action": {
                    "name": "process_event",
                    "config": {
                        "type": action,
                        "publish": True,
                        "allow_anonymous_users": True
                    }
                }
            }
            continue

        # Parse the self-transition lines
        match_self = re.match(r"(\w+) --> \1 : (\w+) \((manual)\) / (\w+)", line)
        if match_self:
            from_state, event, manual, action = match_self.groups()

            # If the from_state doesn't exist in the dictionary, create it
            if from_state not in state_machine["states"]:
                state_machine["states"][from_state] = {"transitions": {}}

            # Create the self transition with the details in the JSON format
            state_machine["states"][from_state]["transitions"][event] = {
                "next": from_state,
                "manual": True,
                "action": {
                    "name": "process_event",
                    "config": {
                        "type": action,
                        "publish": True,
                        "allow_anonymous_users": True,
                        "model": {},
                        "tools": [
                            {
                                "type": "function",
                                "function": {
                                    "name": "set_additional_question_flag",
                                    "description": "Set true if the discussion with the user is not complete and the user has additional feedback details to provide. If set to false, proceed with processing.",
                                    "strict": True,
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "transition": {
                                                "type": "string",
                                                "enum": ["discuss_feedback"]
                                            },
                                            "require_additional_question_flag": {
                                                "type": "boolean"
                                            }
                                        },
                                        "required": ["transition", "require_additional_question_flag"],
                                        "additionalProperties": False
                                    }
                                }
                            }
                        ],
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    "Your feedback seems brief. Would you like to add more details or clarify any points?"
                                ]
                            }
                        ],
                        "tool_choice": "auto",
                        "max_iteration": 30,
                        "approve": True
                    }
                }
            }
            continue

        # Parse the transition with a condition
        match_condition = re.match(r"(\w+) --> (\w+) : (\w+) \[([\w_]+)\] / (\w+)", line)
        if match_condition:
            from_state, to_state, event, condition, action = match_condition.groups()

            # If the from_state doesn't exist in the dictionary, create it
            if from_state not in state_machine["states"]:
                state_machine["states"][from_state] = {"transitions": {}}

            # Create the transition with the condition
            state_machine["states"][from_state]["transitions"][event] = {
                "next": to_state,
                "condition": {
                    "config": {
                        "type": "function",
                        "function": {
                            "name": "is_stage_completed",
                            "description": "Checks if the feedback discussion stage is complete.",
                            "params": {
                                "transition": "discuss_feedback"
                            }
                        }
                    }
                },
                "action": {
                    "name": "process_event",
                    "config": {
                        "type": action,
                        "publish": True,
                        "allow_anonymous_users": True,
                        "model": {},
                        "tools": [
                            {
                                "type": "function",
                                "function": {
                                    "name": "sentiment_analysis",
                                    "description": "Analyzes the sentiment of the feedback.",
                                    "strict": True,
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "text": {
                                                "type": "string"
                                            }
                                        },
                                        "required": ["text"],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            {
                                "type": "function",
                                "function": {
                                    "name": "entity_extraction",
                                    "description": "Extracts key entities from the feedback.",
                                    "strict": True,
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "text": {
                                                "type": "string"
                                            }
                                        },
                                        "required": ["text"],
                                        "additionalProperties": False
                                    }
                                }
                            }
                        ],
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    "Proceeding with analysis: extract sentiment and key entities from the provided feedback: {{feedback}}"
                                ]
                            }
                        ],
                        "tool_choice": "auto",
                        "max_iteration": 10,
                        "approve": True
                    }
                }
            }
            continue

    return json.dumps(state_machine, indent=2)


def main():
    # Sample input diagram
    diagram = """
    stateDiagram-v2
    [*] --> none
    none --> chat_initialized : initialize_chat / function
    chat_initialized --> assistance_request_received : process_assistance_request / agent
    assistance_request_received --> chat_initialized : process_assistance_request / agent
    assistance_request_received --> end : finish_flow / agent
    end --> [*]
    """

    # Convert the diagram to JSON
    converted_json = convert_state_diagram(diagram)
    print(converted_json)


if __name__ == "__main__":
    main()
