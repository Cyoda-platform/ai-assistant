from common.config.conts import *
from entity.chat.data.data import APP_BUILDING_STACK_KEY, \
    LOGIC_CODE_DESIGN_STR, API_REQUEST_STACK_KEY, ENTITIES_DESIGN_STR

data_deploy_stack = lambda deployment_type: \
    [
        {"question": "The env deployment has been scheduled successfully, we'll let you know when it is ready",
         "prompt": {},
         "answer": None,
         "function": None,
         "index": 2,
         "iteration": 0,
         "max_iteration": 0,
         "stack": APP_BUILDING_STACK_KEY,
         "publish": True},
        {"question": None,
         "prompt": {},
         "answer": f"Request to deploy {deployment_type}",
         "function": {"name": "deploy_app",
                      "input": {"deployment_type": deployment_type},
                      "output": {"build_id": ""}},
         "iteration": 0,
         "flow_step": ENTITIES_DESIGN_STR,
         "max_iteration": 0,
         "stack": APP_BUILDING_STACK_KEY,
         }
    ]
