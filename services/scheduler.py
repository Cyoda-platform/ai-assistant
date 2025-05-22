import asyncio
import logging
from typing import List

from common.config import const
from common.config.config import config
from common.config.const import SCHEDULER_STATUS_WAITING
from common.utils.chat_util_functions import _launch_transition
from common.utils.utils import send_cyoda_request
from entity.model import SchedulerEntity

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, entity_service, cyoda_auth_service):
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
        self.backoff_delay = 30  # seconds
        self.max_backoff = 3 * 60  # 3 minutes

    async def start_scheduler(self):
        delay = self.backoff_delay
        while True:
            try:
                scheduled_entities = await self.entity_service.get_items_by_condition(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.SCHEDULER_ENTITY.value,
                    entity_version=config.ENTITY_VERSION,
                    condition={
                        "cyoda": {
                            "type": "group",
                            "operator": "AND",
                            "conditions": [
                                {
                                    "field": "state",
                                    "operatorType": "EQUALS",
                                    "value": SCHEDULER_STATUS_WAITING,
                                    "type": "lifecycle",
                                }
                            ],
                        }
                    })

                if scheduled_entities:
                    delay = self.backoff_delay  # reset delay
                    tasks = [self._run_for_entity(entity) for entity in scheduled_entities]
                    await asyncio.gather(*tasks)
                else:
                    logger.info("No scheduled entities found. Backing off.")
                    delay = min(delay * 2, self.max_backoff)
            except Exception as e:
                logger.exception(f"Scheduler encountered an error: {e}")

            await asyncio.sleep(delay)

    async def _run_for_entity(self, entity: SchedulerEntity):
        try:
            scheduler_instance = ScheduledEntityRunner(
                entity=entity,
                entity_service=self.entity_service,
                cyoda_auth_service=self.cyoda_auth_service
            )
            await scheduler_instance.run()
        except Exception as e:
            logger.exception(f"Failed to process entity {entity.technical_id}: {e}")


class ScheduledEntityRunner:
    def __init__(self, entity: SchedulerEntity, entity_service, cyoda_auth_service):
        self.entity: SchedulerEntity = entity
        self.scheduled_action = entity.scheduled_action
        self.awaited_entity_ids: List[str] = entity.awaited_entity_ids
        self.technical_id = entity.technical_id
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service

    async def run(self) -> None:
        if self.scheduled_action == config.ScheduledAction.SCHEDULE_ENTITIES_FLOW:
            await self._run_entities_flow()
        else:
            await self._run_deploy_flow()

    async def _run_entities_flow(
            self,
    ) -> None:

        tasks = [
            self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=None,
                entity_version=config.ENTITY_VERSION,
                technical_id=eid
            )
            for eid in self.awaited_entity_ids
        ]
        children = await asyncio.gather(*tasks)

        if all(c.get("current_state", "").startswith(const.TransitionKey.LOCKED_CHAT.value) for c in children):
            await _launch_transition(
                entity_service=self.entity_service,
                technical_id=self.technical_id,
                cyoda_auth_service=self.cyoda_auth_service,
            )
            return

    async def _run_deploy_flow(
            self,
            check_interval: float = config.CHECK_DEPLOY_INTERVAL,
            max_attempts: int = const.MAX_SCHEDULER_POLLS,
    ) -> None:
        attempts = 0
        while True:
            if len(self.awaited_entity_ids) != 1:
                raise Exception("Single build id is required")

            build_id = self.awaited_entity_ids[0]
            status_url = (
                f"{config.DEPLOY_CYODA_ENV_STATUS}?build_id={build_id}"
                if self.scheduled_action == config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY
                else f"{config.DEPLOY_USER_APP_STATUS}?build_id={build_id}"
            )

            resp = await send_cyoda_request(
                cyoda_auth_service=self.cyoda_auth_service,
                method="get",
                base_url=status_url,
                path=''
            )
            deploy_state = resp.get("json", {}).get("state")
            deploy_status = resp.get("json", {}).get("status")

            if deploy_state == "PROCESSING":
                logger.info(f"Deployment status: {deploy_status}; re-checking in {check_interval}s...")
            else:
                scheduled_entity = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.SCHEDULER_ENTITY.value,
                    entity_version=config.ENTITY_VERSION,
                    technical_id=self.technical_id
                )
                transition_map = (
                    config.ACTION_SUCCESS_TRANSITIONS if deploy_status == "SUCCESS"
                    else config.ACTION_FAILURE_TRANSITIONS
                )
                scheduled_entity.triggered_entity_next_transition = transition_map.get(self.scheduled_action)
                await _launch_transition(
                    entity_service=self.entity_service,
                    technical_id=self.technical_id,
                    cyoda_auth_service=self.cyoda_auth_service,
                    entity=scheduled_entity
                )
                return

            attempts += 1
            if attempts >= max_attempts:
                scheduled_entity = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.SCHEDULER_ENTITY.value,
                    entity_version=config.ENTITY_VERSION,
                    technical_id=self.technical_id
                )
                scheduled_entity.triggered_entity_next_transition = config.ACTION_FAILURE_TRANSITIONS.get(
                    self.scheduled_action)
                await _launch_transition(
                    entity_service=self.entity_service,
                    technical_id=self.technical_id,
                    cyoda_auth_service=self.cyoda_auth_service,
                    entity=scheduled_entity
                )
                raise TimeoutError(f"Deploy flow did not exit PROCESSING after {max_attempts} polls.")

            await asyncio.sleep(check_interval)
