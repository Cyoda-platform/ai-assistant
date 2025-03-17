import copy

from common.config.conts import *

from entity.chat.data.data import GATHERING_REQUIREMENTS_STR, APPROVAL_NOTIFICATION, APP_BUILDING_STACK_KEY, \
    LOGIC_CODE_DESIGN_STR, API_REQUEST_STACK_KEY, ENTITIES_DESIGN_STR

data_workflow_add_stack = lambda user_prompt, entity_name: \
    [    {"question": "Please let me know if I can help!",
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "index": 2,
                       "iteration": 0,
                       "file_name": "entity/chat.json",
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True}, # {"question": None,
     #  "function": {"name": "validate_workflow"},
     #  "file_name": f"entity/{entity_name}/workflow.json",
     #  "answer": None,
     #  "index": 0,
     #  "iteration": 0,
     #  "flow_step": LOGIC_CODE_DESIGN_STR,
     #  "max_iteration": 0,
     #  "stack": API_REQUEST_STACK_KEY,
     #  "publish": True},
{"question": None,
#       "function": {"name": "update_workflow_code",
#                    "model_api": {
#                        "model": OPEN_AI,
#                        "temperature": 0.7,
#                        "max_tokens": 10000},
#                    "prompt": {
#                        "text": """
# Please generate processors functions {workflow_processors} and add them to the entity workflow {entity_workflow_code}.
# Processes should have name starting with 'process_' and take only one argument entity.
# entity data example {entity_model}
# """,
#                        "api": {"model": OPEN_AI,
#                                "temperature": 0.7,
#                                "max_tokens": 10000},
#                    },
#                    },
      "prompt": {
          "text": f""" # Please implement processors for the newly generated workflow according to the user requirement {user_prompt}.
If the requirement is not specific enough just add a template with example code.
Generate new process functions if necessary or update existing functions according to the user requirement.     
Processes should have name starting with 'process_' and take only one argument entity.
Example:
async def process_some_name(entity: dict):
    final_result = do_some_user_request(...)
    entity["final_result"] = final_result
    entity["workflowProcessed"] = True
""",
          "api": {"model": OPEN_AI,
                  "temperature": 0.7,
                  "max_tokens": 10000}
      },
      "file_name": f"entity/{entity_name}/workflow.py",
      "answer": None,
      "index": 0,
      "iteration": 0,
      "flow_step": LOGIC_CODE_DESIGN_STR,
      "max_iteration": 0,
      "stack": API_REQUEST_STACK_KEY,
      "publish": True},
        {"question": None,
         "prompt": {
             "text": f"""Please construct workflow json from this description/code/flow chart {user_prompt}  using a typical finite-state machine (FSM) model.
The FSM consists of states and transitions between them, which can be represented as a directed graph where states are nodes, and transitions are edges.
Each transition may have processes. Each process starts with 'process_' prefix. Ideally 1 transition:1 process. If the user does not specify processes or their absence explicitly, derive process name from transition name (unless the user explicitly says that processors/functions are not needed).  You need to add them if the user explicitly specifies them. Currently there can be only one transition coming from a single state.
Each state, except for the initial state (None), should be reachable from exactly one transition, ensuring that there are no isolated (disconnected) states in the workflow. Additionally, each transition must have both a start state and an end state.

Begin with an initial state labeled "None", which serves as the origin point.
Define transitions between states, with each state being an endpoint (i.e., target) of exactly one transition.
Ensure that all states (except "None") serve as the destination for exactly one transition to guarantee the graph remains fully connected.

JSON Example of the Workflow:
json
{{
  "name": "specify_name_that_describes_the_workflow",
  "description": "describe_the_workflow",
  "transitions": [
    {{
      "name": "spark_happy_message",
      "description": "Spark the happy message",
      "start_state": "None",
      "start_state_description": "Initial state",
      "end_state": "Happy_message_sparked",
      "end_state_description": "A happy message has been sparked",
      "automated": true
    }},
    {{
      "name": "send_happy_message",
      "description": "Send the happy message",
      "start_state": "Happy_message_sparked",
      "start_state_description": "A happy message has been sparked",
      "end_state": "Message_sent",
      "end_state_description": "The happy message has been sent",
      "automated": true #always put automated true
      "processes": {{
        "schedule_transition_processors": [],
        "externalized_processors": [
          {{
            "name": "process_example",
            "description": ""
          }}
        ]
      }}
    }}
  ]
}}
Please ensure that each process function is referenced in processes.externalized_processors 
Please return only valid json without any additional information.
""",
             "api": {"model": OPEN_AI,
                     "temperature": 0.7,
                     "max_tokens": 10000}
         },
         "answer": user_prompt,
         "file_name": f"entity/{entity_name}/workflow.json",
         "function": None,
         "iteration": 0,
         "flow_step": GATHERING_REQUIREMENTS_STR,
         "max_iteration": 0,
         "stack": APP_BUILDING_STACK_KEY,
         "publish": True}]
