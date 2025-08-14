Get the list of entities with 'list_directory_files' tool.

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
              "executionMode": "SYNC",
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
