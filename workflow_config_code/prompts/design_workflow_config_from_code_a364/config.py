"""
DesignWorkflowConfigFromCodeA364PromptConfig Configuration

Generated from config: workflow_configs/prompts/design_workflow_config_from_code_a364/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Now that you've outlined the workflow from the prototype code, please,
generate workflow configuration json that represents the business workflow of the entity that can be executed on the entity persistence event and call add_application_resource
The FSM json should consist of an ordered dictionary of states. Each state has a list of transitions. Each transition has a next attribute, with the next state.
Each transition may have an processor (it represents a processor java class name which will have processing logic).
Each transition may have a criterion (it represents a criterion java class name which will have processing logic).
Always start from an initial state 'none'.
 Avoid loops. 
If we have multiple transitions from one state, each transition should have a condition to decide which to use


CRITICAL: Processor name is unique per workflow, never reuse it.
 Max 3 processors per workflow.
 It is ok not to have any processors in the workflow for business entities.
 An orchestration entity like 'Job' or 'Task' should have more than one processors.
 If you add one processor to the workflow you should call it '{EntityName}Processor'
 It is ok to have more transitions than processors. Actually your workflow can be very interesting, but have only one processor. You do not need a processor for each transition - it is recommended to have zero to one processor per business entity workflow, and one to three processors per orchestration entity workflow.
 At least one business entity workflow should have one criteria.

Please construct workflow JSON using a typical FSM model based on your previous observations.

JSON Example of the Workflow:
{{
  "version": "1.0",
  "name": "Customer Workflow",
  "desc": "Description of the workflow",
  "initialState": "none",
  "active": true,
  "states": {{
    "none": {{
      "transitions": [
        {{
          "name": "transition_to_01",
          "next": "state_01"
          "manual": false -- always false
        }}
      ]
    }},
    "state_01": {{
      "transitions": [
        {{
          "name": "transition_to_02",
          "next": "state_02",
          "manual": false -- always false
          "processors": [
            {{
              "name": "ProcessorClassName", -- use camel case like a class name. Single word, no special characters.
              "executionMode": "SYNC",
              "config": {{
                "calculationNodesTags": "cyoda_application" <-- always use this tag
              }}
            }}
          ]
        }}
      ]
    }},
    "state_02": {{
      "transitions": [
        {{
          "name": "transition_with_criterion_simple",
          "next": "state_criterion_check_01",
          "manual": false -- always false
          "criterion": {{
            "type": "function",
            "function": {{
              "name": "CriterionClassName",  -- use camel case like a class name. Single word, no special characters.
              "config": {{
                "calculationNodesTags": "cyoda_application"<-- always use this tag
              }}
            }}
          }}
        }}
      ]
    }}
  }}
}}
Return only valid JSON without any extra text or markdown. Return states ordered for the best human readability, like an ordered dictionary."""
