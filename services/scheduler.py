import asyncio
import logging
import common.config.const as const

from common.config.config import ENTITY_VERSION, CHECK_DEPLOY_INTERVAL, DEPLOY_CYODA_ENV_STATUS, DEPLOY_USER_APP_STATUS, \
    ScheduledAction, ACTION_SUCCESS_TRANSITIONS, ACTION_FAILURE_TRANSITIONS
from common.utils.chat_util_functions import _launch_transition
from common.utils.utils import send_cyoda_request
from entity.model import SchedulerEntity

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

    async def _run_entities_flow(
            self,
            check_interval: float = const.SCHEDULER_CHECK_INTERVAL,
            max_attempts: int = const.MAX_SCHEDULER_POLLS,
    ) -> None:
        """Wait until all child entities are LOCKED_CHAT, then launch transition,
        but give up after max_attempts polls."""
        attempts = 0
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

            if all(c.get("current_state").startswith(const.LOCKED_CHAT) for c in children):
                await _launch_transition(
                    entity_service=self.entity_service,
                    technical_id=self.technical_id,
                    cyoda_auth_service=self.cyoda_auth_service,
                )
                return

            attempts += 1
            if attempts >= max_attempts:
                raise TimeoutError(
                    f"Entities flow did not reach LOCKED_CHAT after {max_attempts} polls."
                )

            await asyncio.sleep(check_interval)

    async def _run_deploy_flow(
            self,
            check_interval: float = CHECK_DEPLOY_INTERVAL,
            max_attempts: int = const.MAX_SCHEDULER_POLLS,
    ) -> None:
        """Poll the deploy status endpoint until the build finishes,
        but fail after max_attempts polls."""
        attempts = 0
        while True:
            if len(self.awaited_entity_ids) != 1:
                raise Exception("Single build id is required")

            # choose the right status URL
            if self.scheduled_action == ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY:
                status_url = f"{DEPLOY_CYODA_ENV_STATUS}?build_id={self.awaited_entity_ids[0]}"
            else:
                status_url = f"{DEPLOY_USER_APP_STATUS}?build_id={self.awaited_entity_ids[0]}"

            resp = await send_cyoda_request(
                cyoda_auth_service=self.cyoda_auth_service,
                method="get",
                base_url=status_url,
                path=''
            )
            deploy_state = resp.get("json").get("state")

            if deploy_state == "PROCESSING":
                logger.info(
                    f"Deployment status: {resp.get('status')}; "
                    f"re-checking in {check_interval}s..."
                )
            else:
                scheduled_entity: SchedulerEntity = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.SCHEDULER_ENTITY,
                    entity_version=ENTITY_VERSION,
                    technical_id=self.technical_id
                )
                # Determine whether we succeeded or failed
                deploy_status = resp.get("json").get("status")
                transition_map = (
                    ACTION_SUCCESS_TRANSITIONS
                    if deploy_status == "SUCCESS"
                    else ACTION_FAILURE_TRANSITIONS
                )
                scheduled_entity.triggered_entity_next_transition = \
                    transition_map.get(self.scheduled_action)

                await _launch_transition(
                    entity_service=self.entity_service,
                    technical_id=self.technical_id,
                    cyoda_auth_service=self.cyoda_auth_service,
                    entity=scheduled_entity
                )
                return

            attempts += 1
            if attempts >= max_attempts:
                scheduled_entity: SchedulerEntity = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.SCHEDULER_ENTITY,
                    entity_version=ENTITY_VERSION,
                    technical_id=self.technical_id
                )
                scheduled_entity.triggered_entity_next_transition = ACTION_FAILURE_TRANSITIONS.get(self.scheduled_action)

                await _launch_transition(
                    entity_service=self.entity_service,
                    technical_id=self.technical_id,
                    cyoda_auth_service=self.cyoda_auth_service,
                    entity=scheduled_entity
                )
                raise TimeoutError(
                    f"Deploy flow did not exit PROCESSING after {max_attempts} polls."
                )

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
