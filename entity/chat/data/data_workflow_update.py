import copy

from common.config.conts import *
from common.config.config import MAX_ITERATION
from entity.chat.data.data import GATHERING_REQUIREMENTS_STR, APPROVAL_NOTIFICATION, APP_BUILDING_STACK_KEY, \
    LOGIC_CODE_DESIGN_STR, API_REQUEST_STACK_KEY, ENTITIES_DESIGN_STR

data_workflow_update_stack = lambda workflow_json, user_prompt, entity_name, entity_model: \
    [{"question": "Please let me know if I can help!",
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "index": 2,
                       "iteration": 0,
                       "file_name": "entity/chat.json",
                       "max_iteration": 0,
                       "stack": APP_BUILDING_STACK_KEY,
                       "publish": True},
     {"question": None,
      "prompt": {
          "text": "Please return fully functioning workflow.py code taking into account user suggestions if any.",
          "api": {"model": OPEN_AI,
                  "temperature": 0.7,
                  "max_tokens": 10000},
          "attached_files": [
              f"entity/{entity_name}/workflow.py"]
      },
      "file_name": f"entity/{entity_name}/workflow.py",
      "answer": None,
      "function": None,
      "iteration": 0,
      "flow_step": GATHERING_REQUIREMENTS_STR,
      "max_iteration": MAX_ITERATION,
      "additional_questions": [
          {"question": f"{APPROVAL_NOTIFICATION}",
           "approve": True}],
      "stack": APP_BUILDING_STACK_KEY,
      "publish": True},
     {
         "question": """The new version of the workflow code is ready. Would you like to make any changes? Please approve to proceed to the next step.
""",
         "prompt": None,
         "answer": None,
         "function": None,
         "iteration": 0,
         "flow_step": GATHERING_REQUIREMENTS_STR,
         "max_iteration": 0,
         "approve": True,
         "stack": APP_BUILDING_STACK_KEY,
         "publish": True},
     {"question": None,
      "prompt": {
          "text": f""" # Please update processors functions according the new requirement "{user_prompt}".
Generate new process functions if necessary or update existing functions according to the user requirement.     
Processes should have name starting with 'process_' and take only one argument entity.
Entity data example {entity_model}""",
          "api": {"model": OPEN_AI,
                  "temperature": 0.7,
                  "max_tokens": 10000},
          "attached_files": [f"entity/{entity_name}/workflow.py", f"entity/{entity_name}/workflow.json"]
      },
      "file_name": f"entity/{entity_name}/workflow.py",
      "answer": None,
      "index": 0,
      "iteration": 0,
      "flow_step": LOGIC_CODE_DESIGN_STR,
      "max_iteration": 0,
      "stack": API_REQUEST_STACK_KEY,
      "publish": True},
     # {"question": None,
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
      "prompt": {
          "text": "Please return complete workflow.json taking into account user suggestions if any.",
          "api": {"model": OPEN_AI,
                  "temperature": 0.7,
                  "max_tokens": 10000},
          "attached_files": [
              f"entity/{entity_name}/workflow.json"]
      },
      "file_name": f"entity/{entity_name}/workflow.json",
      "answer": None,
      "function": None,
      "iteration": 0,
      "flow_step": GATHERING_REQUIREMENTS_STR,
      "max_iteration": MAX_ITERATION,
      "additional_questions": [
          {"question": f"{APPROVAL_NOTIFICATION}",
           "approve": True}],
      "stack": APP_BUILDING_STACK_KEY,
      "publish": True},
     {
         "question": """The new version of the workflow is ready. Would you like to make any changes? Please approve to proceed to the next step.
""",
         "prompt": None,
         "answer": None,
         "function": None,
         "iteration": 0,
         "flow_step": GATHERING_REQUIREMENTS_STR,
         "max_iteration": 0,
         "approve": True,
         "stack": APP_BUILDING_STACK_KEY,
         "publish": True},
     {"question": None,
      "prompt": {
          "text": f""" You are provided entity workflow json {workflow_json}. Please update it based on the user request "{user_prompt}"        
Processes should have name starting with 'process_'. Please return only workflow json only""",
          "api": {"model": OPEN_AI,
                  "temperature": 0.7,
                  "max_tokens": 10000},
          "attached_files": [f"entity/{entity_name}/workflow.json"]
      },
      "file_name": f"entity/{entity_name}/workflow.json",
      "answer": user_prompt,
      "index": 0,
      "iteration": 0,
      "flow_step": LOGIC_CODE_DESIGN_STR,
      "max_iteration": 0,
      "stack": API_REQUEST_STACK_KEY,
      "publish": True}]