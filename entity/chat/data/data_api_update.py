from common.config.conts import *
from common.config.config import MAX_ITERATION
from entity.chat.data.data import GATHERING_REQUIREMENTS_STR, APPROVAL_NOTIFICATION, APP_BUILDING_STACK_KEY, \
    LOGIC_CODE_DESIGN_STR, API_REQUEST_STACK_KEY

data_api_update_stack = lambda user_prompt, entity_name: \
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
          "text": "Please return complete app.py taking into account user suggestions if any.",
          "api": {"model": OPEN_AI,
                  "temperature": 0.7,
                  "max_tokens": 10000},
          "attached_files": [
              f"app.py"]
      },
      "file_name": f"app.py",
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
         "question": """The new version of the api is ready. Would you like to make any changes? Please approve to proceed to the next step.
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
          "text": f""" You are provided with code that implements a REST API (using a framework Quart).
Please update it according to the user request: {user_prompt}

Reference: 
entity_service (from app_init.app_init import entity_service).
You can use only these functions for replacement - if this is not enough just skip and leave as is
1.
id = await entity_service.add_item(
    token=cyoda_token,
    entity_model="{entity_name}",
    entity_version=ENTITY_VERSION,  # always use this constant
    entity=data  # the validated data object
)
just return id in the response - you cannot immediately retrieve the result - it should be retrieved via separate endpoint
2. Data retrieval: 
await entity_service.get_item(
    token=cyoda_token,
    entity_model="{entity_name}",
    entity_version=ENTITY_VERSION,
    technical_id=<id>
)
await entity_service.get_items(
    token=cyoda_token,
    entity_model="{entity_name}",
    entity_version=ENTITY_VERSION,
)
await entity_service.get_items_by_condition(
    token=cyoda_token,
    entity_model="{entity_name}",
    entity_version=ENTITY_VERSION,
    condition=condition
)
3. 
await entity_service.update_item(
    token=cyoda_token,
    entity_model="{entity_name}",
    entity_version=ENTITY_VERSION,  # always use this constant
    entity=data,
    technical_id=id,
    meta={{}}
)
4.
await entity_service.delete_item(
    token=cyoda_token,
    entity_model="{entity_name}",
    entity_version=ENTITY_VERSION,  # always use this constant
    technical_id=id,
    meta={{}}
)""",
          "api": {"model": OPEN_AI_o3,
                  "temperature": 0.7,
                  "max_tokens": 10000},
          "attached_files": [f"app.py"]
      },
      "file_name": f"app.py",
      "answer": user_prompt,
      "index": 0,
      "iteration": 0,
      "flow_step": LOGIC_CODE_DESIGN_STR,
      "max_iteration": 0,
      "stack": API_REQUEST_STACK_KEY,
      "publish": True}]