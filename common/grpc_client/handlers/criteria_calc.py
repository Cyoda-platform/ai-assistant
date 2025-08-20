import json
import logging

from cloudevents_pb2 import CloudEvent

from common.grpc_client.handlers.base import Handler
from common.grpc_client.responses.spec import ResponseSpec
from common.grpc_client.constants import CRITERIA_CALC_REQ_EVENT_TYPE, CRITERIA_CALC_RESP_EVENT_TYPE
from entity.model import WorkflowEntity
from entity.model_registry import model_registry

logger = logging.getLogger(__name__)


class CriteriaCalcRequestHandler(Handler):
    async def handle(self, request: CloudEvent, services=None):
        data = json.loads(request.text_data)
        criteria_name = data.get('criteriaName')

        model_key = data['payload']['meta']['modelKey']['name']
        model_cls = model_registry.get(model_key, WorkflowEntity)

        entity = model_cls.model_validate(data['payload']['data'])
        entity.current_transition = data['transition']['name']

        matches = None
        try:
            logger.info(f"[PROCESSING] Starting {CRITERIA_CALC_REQ_EVENT_TYPE} - Criteria: {criteria_name}, EntityId: {data['entityId']}, RequestId: {data.get('requestId')}")

            # Use workflow_dispatcher from services
            workflow_dispatcher = services.workflow_dispatcher if services else None
            if not workflow_dispatcher:
                raise ValueError("workflow_dispatcher not available in services")

            entity, matches = await workflow_dispatcher.process_event(
                entity=entity,
                processor_name=criteria_name,
                payload=data,
                technical_id=data['entityId'])
            data['payload']['data'] = model_cls.model_dump(entity)
            logger.info(f"[PROCESSING] Success {CRITERIA_CALC_REQ_EVENT_TYPE} - Criteria: {criteria_name}, EntityId: {data['entityId']}")
        except Exception as e:
            logger.error(f"[PROCESSING] Error {CRITERIA_CALC_REQ_EVENT_TYPE} - Criteria: {criteria_name}, EntityId: {data['entityId']}")
            logger.exception("Error processing entity", exc_info=e)
            entity.failed = True
            data['payload']['data'] = model_cls.model_dump(entity)
            matches = False

        return ResponseSpec(
            response_type=CRITERIA_CALC_RESP_EVENT_TYPE,
            data={
                "requestId": data.get('requestId'),
                "entityId": data.get('entityId'),
                "matches": matches,
            },
            success=True,
        )

