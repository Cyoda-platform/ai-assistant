import json
import sys


def convert_to_mermaid(data):
    """
    Convert the workflow configuration to a Mermaid state diagram string.
    """
    initial_state = data.get("initial_state")
    states = data.get("states", {})
    lines = ["stateDiagram-v2"]

    # Define the initial state arrow
    if initial_state:
        lines.append(f"    [*] --> {initial_state}")

    # Process each state and its transitions
    for state, state_info in states.items():
        transitions = state_info.get("transitions", {})
        for trigger, transition in transitions.items():
            next_state = transition.get("next", "")
            condition = transition.get("condition", {}).get("config", {}).get("function", {}).get("name")
            action = transition.get("action", {}).get("config", {}).get("type")
            manual = transition.get("manual", False)

            # Build the label for the transition
            label_parts = [trigger]
            if condition:
                label_parts.append(f"/condition [{condition}]")
            if manual:
                label_parts.append("(manual)")
            if action:
                label_parts.append(f"/{action}")
            label = " ".join(label_parts)

            # Create the mermaid line for this transition
            lines.append(f"    {state} --> {next_state} : {label}")
    lines.append(f"    end --> [*]")
    return "\n".join(lines)


def main():
    filename = "workflow.json"

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)

    mermaid_diagram = convert_to_mermaid(data)
    print(mermaid_diagram)


if __name__ == "__main__":
    main()