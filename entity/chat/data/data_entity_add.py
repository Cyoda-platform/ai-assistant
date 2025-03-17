import copy

from common.config.conts import *

from entity.chat.data.data import GATHERING_REQUIREMENTS_STR, APP_BUILDING_STACK_KEY, ENTITIES_DESIGN_STR

data_entity_add_stack = lambda user_prompt, entity_name: \
    [ {"question": "Please let me know if I can help!",
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
             "text": f"""Please add data model example for the {entity_name} according to the user_requirement: {user_prompt} . Please return raw data example and not schema""",
             "api": {"model": REQUIREMENT_AGENT,
                     "temperature": 0.7,
                     "max_tokens": 10000}
         },
         "answer": user_prompt,
         "file_name": f"entity/{entity_name}/{entity_name}.json",
         "function": None,
         "iteration": 0,
         "flow_step": GATHERING_REQUIREMENTS_STR,
         "max_iteration": 0,
         "stack": APP_BUILDING_STACK_KEY,
         "publish": True}
    ]
