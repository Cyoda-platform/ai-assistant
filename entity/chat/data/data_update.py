from common.config.conts import *
from entity.chat.data.data import APP_BUILDING_STACK_KEY, \
    LOGIC_CODE_DESIGN_STR, API_REQUEST_STACK_KEY, ENTITIES_DESIGN_STR

data_answer_question = lambda user_prompt: \
    [{"question": """
Please let me know if I can help!
""",
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
          "text": f"""{user_prompt}""",
          "api": {"model": OPEN_AI,
                  "temperature": 0.7,
                  "max_tokens": 10000},
      },
      "answer": None,
      "index": 0,
      "iteration": 0,
      "flow_step": LOGIC_CODE_DESIGN_STR,
      "max_iteration": 0,
      "stack": API_REQUEST_STACK_KEY,
      "publish": True}]

data_update_stack = lambda app_api, entities_description, user_prompt: \
    [{"question": """
Examples to proceed:

Please, add a new entity for ...
Please, add a workflow for ...

Please let me know if I can help!
""",
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
          "text": f"""
Please analyse the user requirement and provide a modification plan for the existing application.
Cyoda application organises logic around entities with attached workflows. Data is abstracted into entity.
Code (logic) is abstracted into workflow external processors. Such workflow is triggered right before the entity is saved and can modify entity data, so that only the uppdated data is saved.
Workflow processors code can also work with other entities via entity_service.

Currently we have the following entities with the following workflow processors attached {entities_description} 

You are also provided with the app.py containing application endpoints {app_api}.

User requirement: "{user_prompt}"

Please return the answer in the following format:
In order to implement this requirement,
I can suggest introducing a new entity *entity_name*/ reusing the existing entity *entity_name*.

Then I recommend to add a new workflow/update the existing entity workflow to incorporate the following logic: *specify the logic*
Workflow mermaid flowchart diagram example:

""",
          "api": {"model": OPEN_AI,
                  "temperature": 0.7,
                  "max_tokens": 10000},
      },
      "answer": user_prompt,
      "index": 0,
      "iteration": 0,
      "flow_step": LOGIC_CODE_DESIGN_STR,
      "max_iteration": 0,
      "stack": API_REQUEST_STACK_KEY,
      "publish": True}]
