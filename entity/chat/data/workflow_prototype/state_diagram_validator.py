import re

def validate_state_diagram(diagram: str) -> list:
    errors = []
    lines = diagram.splitlines()
    # Remove empty lines and strip whitespace
    lines = [line.strip() for line in lines if line.strip()]
    if not lines:
        errors.append("Diagram is empty.")
        return errors

    # 1. Check for stateDiagram declaration in the first non-empty line.
    if not lines[0].startswith("stateDiagram"):
        errors.append("The diagram must start with 'stateDiagram'.")

    # 2. Check for a direction line with a valid direction.
    direction_found = False
    valid_directions = {"TB", "BT", "LR", "RL"}
    for line in lines:
        if line.startswith("direction"):
            direction_found = True
            parts = line.split()
            if len(parts) < 2:
                errors.append("Direction line is malformed.")
            else:
                if parts[1] not in valid_directions:
                    errors.append(f"Invalid direction '{parts[1]}'. Valid directions are: {', '.join(valid_directions)}.")
            break
    if not direction_found:
        errors.append("Direction line not found.")

    # 3. Define a regex pattern for transition lines.
    # The pattern captures:
    # - source state
    # - target state
    # - optional transition label (which may include a (manual) flag)
    # - optional action type and action details (enclosed in square brackets)
    transition_pattern = re.compile(
        r'^(?P<source>\S(?:.*?\S)?)\s*-->\s*(?P<target>\S(?:.*?\S)?)'
        r'(?:\s*:\s*(?P<label>[^/(\[]]+?)(?:\s*\((?P<manual>manual)\))?\s*)?)?'
        r'(?:/\s*(?P<action_type>\w+)\s*(?P<action_details>\[.*\]))?\s*$'
    )

    transitions = []  # List of (source, target) tuples.
    graph_edges = []  # For connectivity check.
    # Process each line (skip lines that are the stateDiagram and direction lines)
    for i, line in enumerate(lines[1:], start=2):  # starting count at line 2 for clarity
        if line.startswith("stateDiagram") or line.startswith("direction"):
            continue

        match = transition_pattern.match(line)
        if not match:
            errors.append(f"Line {i}: Transition format invalid: '{line}'")
            continue

        groups = match.groupdict()
        source = groups.get("source")
        target = groups.get("target")
        label = groups.get("label")
        manual_flag = groups.get("manual")
        action_type = groups.get("action_type")
        action_details = groups.get("action_details")

        # Validate source and target are not empty.
        if not source:
            errors.append(f"Line {i}: Source state is empty.")
        if not target:
            errors.append(f"Line {i}: Target state is empty.")

        # If a colon is present in the line, ensure that a label exists.
        if ":" in line:
            if label is None or label.strip() == "":
                errors.append(f"Line {i}: Transition label is missing after colon.")

        # Validate action type if present.
        if action_type:
            valid_action_types = {"notification", "function", "question", "agent", "prompt"}
            if action_type not in valid_action_types:
                errors.append(f"Line {i}: Invalid action type '{action_type}'. Valid types are: {', '.join(valid_action_types)}.")

        # Validate action details: must start with '[' and end with ']'
        if action_details:
            if not (action_details.startswith("[") and action_details.endswith("]")):
                errors.append(f"Line {i}: Action details must be enclosed in '[' and ']'.")

        transitions.append((source, target))
        graph_edges.append((source, target))

    # 4. Build a graph from the transitions to check connectivity.
    graph = {}
    for source, target in graph_edges:
        graph.setdefault(source, set()).add(target)
        # Ensure all nodes appear in the graph.
        if target not in graph:
            graph[target] = set()

    # 5. Validate the existence of the initial and terminal states.
    # Initial state: a transition must start from "[*]".
    initial_exists = any(src.strip() == "[*]" for src, _ in transitions)
    if not initial_exists:
        errors.append("Initial state '[*]' not defined as a source in any transition.")

    # Terminal state: a transition must end with "[*]".
    terminal_exists = any(tgt.strip() == "[*]" for _, tgt in transitions)
    if not terminal_exists:
        errors.append("Terminal state '[*]' not defined as a target in any transition.")

    # 6. Check connectivity: Ensure all states are reachable from the initial state "[*]".
    if initial_exists:
        visited = set()
        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            for neighbor in graph.get(node, []):
                dfs(neighbor)
        dfs("[*]")
        for state in graph.keys():
            if state not in visited:
                errors.append(f"Orphan state detected: '{state}' is not reachable from the initial state '[*]'.")

    return errors

# Example usage:
if __name__ == "__main__":
    sample_diagram = """
    stateDiagram
      direction TB
      [*] --> none
      none --> greeting_sent: welcome_user / notification [Welcome!]
      greeting_sent --> repository_cloned: clone_repo / function [clone_repo]
      repository_cloned --> chats_established: init_chats / function [init_chats]
      chats_established --> app_requirements_requested: request_application_requirements / question []
      app_requirements_requested --> app_requirements_requested: process_application_requirement (manual) / agent [web_search(query="search_query")],[read_link(url="")], [web_scrape(url="<url>", selector="<css_selector>" )], [set_additional_question_flag(transition="process_application_requirement", require_additional_question_flag=true)]
      app_requirements_requested --> app_requirements_finalized: process_application_requirement_success [is_stage_completed(transition="process_application_requirement", require_additional_question_flag=false)]
      app_requirements_finalized --> workflow_state_question: request_workflow_state_diagram / question []
      workflow_state_question --> workflow_state_question: discuss_workflow_state (manual) / agent [web_search(query="search_query")],[read_link(url="")], [web_scrape(url="<url>", selector="<css_selector>" )], [set_additional_question_flag(transition="discuss_workflow_state", require_additional_question_flag=true)]
      workflow_state_question --> workflow_state_finalized: workflow_state_diagram_finalized [is_stage_completed(transition="discuss_workflow_state", require_additional_question_flag=false)]
      workflow_state_finalized --> workflow_json_generated: generate_workflow_json / function [generate_workflow_json]
      workflow_json_generated --> workflow_function_requirement_received: request_workflow_function_generation / question []
      workflow_function_requirement_received --> workflow_function_requirement_received: discuss_workflow_functions (manual) / agent [web_search(query="search_query")],[read_link(url="")], [web_scrape(url="<url>", selector="<css_selector>" )], [set_additional_question_flag(transition="discuss_workflow_functions", require_additional_question_flag=true)]
      workflow_function_requirement_received --> workflow_functions_generated: workflow_functions_generated [is_stage_completed(transition="discuss_workflow_functions", require_additional_question_flag=false)]
      workflow_functions_generated --> started_general_discussion: request_general_questions / question []
      started_general_discussion --> started_general_discussion: process_question (manual) / agent [web_search(query="search_query")],[read_link(url="")], [web_scrape(url="<url>", selector="<css_selector>" )], [set_additional_question_flag(transition="process_question", require_additional_question_flag=true)]
      started_general_discussion --> workflow_completed: process_question_success [is_stage_completed(transition="process_question", require_additional_question_flag=false)]
      workflow_completed --> end: finalize_workflow / prompt []
      end --> [*]
    """

    validation_errors = validate_state_diagram(sample_diagram)
    if validation_errors:
        print("Validation Errors:")
        for error in validation_errors:
            print(f" - {error}")
    else:
        print("State diagram is valid.")
