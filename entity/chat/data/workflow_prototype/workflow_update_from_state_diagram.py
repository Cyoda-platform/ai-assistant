import re
import sys


def extract_states(diagram_text):
    """
    Extracts state names from a state diagram text.
    It looks for transitions of the form:
      <from_state> --> <to_state> [ : <action> / <event> ]
    and returns a list of states in the order they first appear, ignoring the [*] marker.
    """
    states = []
    for line in diagram_text.strip().splitlines():
        line = line.strip()
        # Match transitions; this assumes state names are non-space tokens.
        match = re.match(r'(\S+)\s*-->\s*(\S+)', line)
        if match:
            from_state = match.group(1)
            to_state = match.group(2)
            if from_state != "[*]" and from_state not in states:
                states.append(from_state)
            if to_state not in states:
                states.append(to_state)
    return states


def replace_states(content, mapping):
    """
    Replace each occurrence of a version1 state name in content with its corresponding
    version2 name using word boundaries.
    """
    # For each key in the mapping, do a regex replacement.
    for old_state, new_state in mapping.items():
        # Use word boundaries to ensure only whole words are replaced.
        pattern = r'\b{}\b'.format(re.escape(old_state))
        content = re.sub(pattern, new_state, content)
    return content


def main():

    version1_file = "/home/kseniia/PycharmProjects/ai_assistant/entity/chat/data/workflow_prototype/workflow_diagram.txt"
    version2_file = "/home/kseniia/PycharmProjects/ai_assistant/entity/chat/data/workflow_prototype/workflow_diagram_2.txt"
    input_file = "/home/kseniia/PycharmProjects/ai_assistant/entity/chat/data/workflow_prototype/workflow_updated.json"

    # Read file contents
    with open(version1_file, 'r') as f:
        version1_text = f.read()

    with open(version2_file, 'r') as f:
        version2_text = f.read()

    with open(input_file, 'r') as f:
        input_content = f.read()

    # Extract state names from both versions.
    states_v1 = extract_states(version1_text)
    states_v2 = extract_states(version2_text)

    # Build mapping: version1 state -> version2 state.
    mapping = {s1: s2 for s1, s2 in zip(states_v1, states_v2)}

    # Replace state names in the input file using the mapping.
    replaced_content = replace_states(input_content, mapping)

    # Output the mapping and the replaced content.
    print("Mapping of state names from version 1 to version 2:")
    print(mapping)
    print("\nReplaced content:")
    print(replaced_content)


if __name__ == "__main__":
    main()
