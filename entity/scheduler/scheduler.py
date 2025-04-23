import asyncio

from common.config.config import ENTITY_VERSION
from common.config.conts import SCHEDULER_CHECK_INTERVAL, LOCKED_CHAT
from common.util.chat_util_functions import _launch_transition


class WorkflowTask:
    """
    Encapsulates a workflow task that repeatedly checks the state of child entities.
    When all entities are 'locked', it triggers a transition.
    """

    def __init__(self, technical_id, awaited_entity_ids, entity_service, cyoda_auth_service):
        self.technical_id = technical_id
        self.awaited_entity_ids = awaited_entity_ids
        self.entity_service = entity_service
        self.cyoda_auth_service=cyoda_auth_service

    async def run(self, CHECK_INTERVAL=SCHEDULER_CHECK_INTERVAL):
        """
        Periodically check (every CHECK_INTERVAL seconds) whether all awaited child entities are locked.
        Once all are locked, trigger the transition and exit the loop.
        """
        while True:
            tasks = [
                self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=None,
                    entity_version=ENTITY_VERSION,
                    technical_id=awaited_id
                )
                for awaited_id in self.awaited_entity_ids
            ]
            child_entities = await asyncio.gather(*tasks)
            if all(child.get("current_state") == LOCKED_CHAT for child in child_entities):
                await _launch_transition(entity_service=self.entity_service,
                                         technical_id=self.technical_id,
                                         cyoda_auth_service=self.cyoda_auth_service)
                break
            else:
                await asyncio.sleep(CHECK_INTERVAL)


class Scheduler:
    """
    Manages workflow tasks: it registers them and keeps track of running tasks.
    """

    def __init__(self, entity_service, cyoda_auth_service):
        self.entity_service = entity_service
        self.tasks = []  # List to hold asyncio.Task objects.
        self.cyoda_auth_service = cyoda_auth_service

    def schedule_workflow_task(self, technical_id, awaited_entity_ids):
        """
        Registers a new workflow task.
        Returns "ok" immediately after scheduling the task in the background.
        """
        workflow_task = WorkflowTask(technical_id=technical_id, awaited_entity_ids=awaited_entity_ids,
                                     entity_service=self.entity_service,
                                     cyoda_auth_service=self.cyoda_auth_service)
        task = asyncio.create_task(workflow_task.run())
        self.tasks.append(task)
        return "ok"
