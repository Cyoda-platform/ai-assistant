from common.config.conts import *
from entity.chat.data.data import APP_BUILDING_STACK_KEY, \
    LOGIC_CODE_DESIGN_STR, API_REQUEST_STACK_KEY, ENTITIES_DESIGN_STR

data_refresh_context_stack = [{"question": "Please let me know if I can help!",
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
      "prompt": {},
      "answer": "Request to refresh the context",
      "function": {"name": "refresh_context",
                   "model_api": {
                       "model": OPEN_AI,
                       "temperature": 0.7}},
      "iteration": 0,
      "flow_step": ENTITIES_DESIGN_STR,
      "max_iteration": 0,
      "stack": APP_BUILDING_STACK_KEY}]
