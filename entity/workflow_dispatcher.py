import copy
import inspect
import logging
from entity.chat.workflow.workflow import ChatWorkflow
from entity.workflow import Workflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowDispatcher:
    def __init__(self, cls, cls_instance, mock=False):
        self.cls = cls
        self.cls_instance = cls_instance
        self.methods_dict = self.collect_subclass_methods()

    def collect_subclass_methods(self):

    # Using inspect.getmembers ensures we only get functions defined on the class
        methods = {}
        for name, func in inspect.getmembers(self.cls, predicate=inspect.isfunction):
            # Create a unique key to avoid collisions
            key = f"{name}"
            methods[key] = func
        return methods


    async def dispatch_function(self, token, event, chat):
        try:
            if event["function"]["name"] in self.methods_dict:
                response = await self.methods_dict[event["function"]["name"]](self.cls_instance,
                                                                              token, copy.deepcopy(event),
                                                                              chat)
            else:
                raise ValueError(f"Unknown processing step: {event["function"]["name"]}")
            return response
        except Exception as e:
            logger.exception(e)
            logger.info(f"Error processing event: {e}")

    async def process_event(self, token, data, processor_name):
        meta = {"token": token, "entity_model": "ENTITY_PROCESSED_NAME", "entity_version": "ENTITY_VERSION"}
        payload_data = data['payload']['data']
        if processor_name in self.methods_dict:
            try:
                response = await self.methods_dict[processor_name](self.cls_instance, meta, payload_data)
            except Exception as e:
                logger.info(f"Error processing event: {e}")
                raise
        else:
            raise ValueError(f"Unknown processing step: {processor_name}")
        return response
