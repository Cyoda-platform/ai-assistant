import asyncio
import logging

from common.config.config import ENTITY_VERSION, CHECK_DEPLOY_INTERVAL, DEPLOY_CYODA_ENV_STATUS, DEPLOY_USER_APP_STATUS, \
    ScheduledAction
from common.config.conts import SCHEDULER_CHECK_INTERVAL, LOCKED_CHAT
from common.util.chat_util_functions import _launch_transition
from common.util.utils import send_cyoda_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowTask:
    """
    Encapsulates a workflow task that repeatedly checks the state of child entities,
    or polls a deploy endpoint, depending on scheduled_action.
    """

    def __init__(
        self,
        technical_id: str,
        awaited_entity_ids: list[str],
        entity_service,
        cyoda_auth_service,
        scheduled_action: ScheduledAction
    ):
        self.technical_id = technical_id
        self.awaited_entity_ids = awaited_entity_ids
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
        self.scheduled_action = scheduled_action

    async def run(self) -> None:
        if self.scheduled_action == ScheduledAction.SCHEDULE_ENTITIES_FLOW:
            await self._run_entities_flow()
        else:
            await self._run_deploy_flow()

    async def _run_entities_flow(self, check_interval: float = SCHEDULER_CHECK_INTERVAL) -> None:
        """Wait until all child entities are LOCKED_CHAT, then launch transition."""
        while True:
            # fetch all children in parallel
            tasks = [
                self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=None,
                    entity_version=ENTITY_VERSION,
                    technical_id=eid
                )
                for eid in self.awaited_entity_ids
            ]
            children = await asyncio.gather(*tasks)
            if all(c.get("current_state") == LOCKED_CHAT for c in children):
                await _launch_transition(
                    entity_service=self.entity_service,
                    technical_id=self.technical_id,
                    cyoda_auth_service=self.cyoda_auth_service,
                )
                return
            await asyncio.sleep(check_interval)

    async def _run_deploy_flow(self, check_interval: float = CHECK_DEPLOY_INTERVAL) -> None:
        """Poll the deploy status endpoint until the build finishes."""
        while True:
            if len(self.awaited_entity_ids) != 1:
                raise Exception("Single build id is required")
            if self.scheduled_action == ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY:
                status_url = f"{DEPLOY_CYODA_ENV_STATUS}?build_id={self.awaited_entity_ids[0]}"
            else:
                status_url = f"{DEPLOY_USER_APP_STATUS}?build_id={self.awaited_entity_ids[0]}"
            resp = await send_cyoda_request(cyoda_auth_service=self.cyoda_auth_service,
                                        method="get",
                                        base_url=status_url,
                                        path='')
            deploy_state = resp.get("json").get("state")
            if deploy_state == "PROCESSING":
                logger.info(
                    f"Deployment status: {resp.get('status')}; "
                    f"re-checking in {check_interval}s..."
                )
            else:
                await _launch_transition(
                    entity_service=self.entity_service,
                    technical_id=self.technical_id,
                    cyoda_auth_service=self.cyoda_auth_service
                )
                return
            await asyncio.sleep(check_interval)

class Scheduler:
    """
    Manages workflow tasks: it registers them and keeps track of running tasks.
    """

    def __init__(self, entity_service, cyoda_auth_service):
        self.entity_service = entity_service
        self.tasks = []  # List to hold asyncio.Task objects.
        self.cyoda_auth_service = cyoda_auth_service

    def schedule_workflow_task(self, technical_id, awaited_entity_ids, scheduled_action: ScheduledAction):
        """
        Registers a new workflow task.
        Returns "ok" immediately after scheduling the task in the background.
        """
        workflow_task = WorkflowTask(technical_id=technical_id,
                                     awaited_entity_ids=awaited_entity_ids,
                                     entity_service=self.entity_service,
                                     cyoda_auth_service=self.cyoda_auth_service,
                                     scheduled_action=scheduled_action)
        task = asyncio.create_task(workflow_task.run())
        self.tasks.append(task)
        return "ok"
