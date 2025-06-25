import asyncio
import logging
from typing import List

from common.config import const
from common.config.config import config
from common.utils.utils import send_cyoda_request
from entity.model import SchedulerEntity

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, entity_service, cyoda_auth_service):
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
        self.backoff_delay = 30  # seconds
        self.max_backoff = 3 * 60  # 3 minutes

    async def run_for_entity(self, technical_id, entity: SchedulerEntity)-> tuple[str, str]:
        scheduler_instance = ScheduledEntityRunner(
            entity=entity,
            technical_id=technical_id,
            entity_service=self.entity_service,
            cyoda_auth_service=self.cyoda_auth_service
        )
        return await scheduler_instance.run()



class ScheduledEntityRunner:
    def __init__(self, entity: SchedulerEntity, technical_id: str, entity_service, cyoda_auth_service):
        self.entity: SchedulerEntity = entity
        self.scheduled_action = entity.scheduled_action
        self.awaited_entity_ids: List[str] = entity.awaited_entity_ids
        self.technical_id = technical_id
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service

    async def run(self)-> tuple[str, str]:
        if self.scheduled_action == config.ScheduledAction.SCHEDULE_ENTITIES_FLOW:
            return await self._run_entities_flow()
        else:
            return await self._run_deploy_flow()

    async def _run_entities_flow(
            self,
    )-> tuple[str, str]:

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
            if all(c.get("current_state", "").startswith(const.TransitionKey.LOCKED_CHAT.value) for c in children):
                return 'complete', ''
        return 'in_progress', ''

    async def _run_deploy_flow(self) -> tuple[str, str]:

        if len(self.awaited_entity_ids) != 1:
            raise Exception("Single build id is required")

        build_id = self.awaited_entity_ids[0]
        status_url = (
            f"{config.DEPLOY_CYODA_ENV_STATUS}?build_id={build_id}"
            if self.scheduled_action == config.ScheduledAction.SCHEDULE_CYODA_ENV_DEPLOY
            else f"{config.DEPLOY_USER_APP_STATUS}?build_id={build_id}"
        )

        try:
            resp = await send_cyoda_request(
                cyoda_auth_service=self.cyoda_auth_service,
                method="get",
                base_url=status_url,
                path=''
            )
        except Exception as e:
            logger.exception(e)
            transition_map = (
                config.ACTION_FAILURE_TRANSITIONS
            )
            await self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.SCHEDULER_ENTITY.value,
                entity_version=config.ENTITY_VERSION,
                technical_id=self.technical_id
            )
            triggered_entity_next_transition = transition_map.get(self.scheduled_action)
            return 'complete', triggered_entity_next_transition
        deploy_state = resp.get("json", {}).get("state")
        deploy_status = resp.get("json", {}).get("status")

        if deploy_state == "PROCESSING":
            return 'in_progress', ''
        else:
            await self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.SCHEDULER_ENTITY.value,
                entity_version=config.ENTITY_VERSION,
                technical_id=self.technical_id
            )
            transition_map = (
                config.ACTION_SUCCESS_TRANSITIONS if deploy_status == "SUCCESS"
                else config.ACTION_FAILURE_TRANSITIONS
            )
            triggered_entity_next_transition = transition_map.get(self.scheduled_action)
            return 'complete', triggered_entity_next_transition
