import logging

import grpc
import uuid
import json
import asyncio
from cloudevents_pb2 import CloudEvent
from common.config import config
from common.config.config import GRPC_PROCESSOR_TAG
from cyoda_cloud_api_pb2_grpc import CloudEventsServiceStub
from entity.chat.model.chat import ChatEntity
from entity.model.model import AgenticFlowEntity, WorkflowEntity
from entity.model.model_registry import model_registry
from entity.workflow import process_dispatch

# These tags are configured in the workflow UI for external processor
TAGS = [GRPC_PROCESSOR_TAG]
OWNER = "PLAY"
SPEC_VERSION = "1.0"
SOURCE = "SimpleSample"
JOIN_EVENT_TYPE = "CalculationMemberJoinEvent"
CALC_RESP_EVENT_TYPE = "EntityProcessorCalculationResponse"
CALC_REQ_EVENT_TYPE = "EntityProcessorCalculationRequest"
CRITERIA_CALC_REQ_EVENT_TYPE = "EntityCriteriaCalculationRequest"
CRITERIA_CALC_RESP_EVENT_TYPE = "EntityCriteriaCalculationResponse"
GREET_EVENT_TYPE = "CalculationMemberGreetEvent"
KEEP_ALIVE_EVENT_TYPE = "CalculationMemberKeepAliveEvent"
EVENT_ACK_TYPE = "EventAckResponse"
EVENT_ID_FORMAT = "{uuid}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrpcClient:
    def __init__(self, workflow_dispatcher):
        self.workflow_dispatcher = workflow_dispatcher

    def create_cloud_event(self, event_id: str, source: str, event_type: str, data: dict) -> CloudEvent:
        """
        Create a CloudEvent instance with the given parameters.

        :param event_id: Unique identifier for the event.
        :param source: Source of the event.
        :param event_type: Type of the event.
        :param data: Data associated with the event.
        :return: A CloudEvent instance.
        """
        return CloudEvent(
            id=event_id,
            source=source,
            spec_version=SPEC_VERSION,
            type=event_type,
            text_data=json.dumps(data)
        )

    def create_join_event(self) -> CloudEvent:
        """
        Create a CloudEvent for a member join event.

        :return: A CloudEvent instance for the join event.
        """
        return self.create_cloud_event(
            event_id=str(uuid.uuid4()),
            source=SOURCE,
            event_type=JOIN_EVENT_TYPE,
            data={"owner": OWNER, "tags": TAGS}
        )

    def create_notification_event(self, data: dict, type: str, response=None) -> CloudEvent:
        """
        Create a CloudEvent for a notification response.

        :param data: Data from the notification response.
        :return: A CloudEvent instance for the notification event.
        """
        if type == CALC_REQ_EVENT_TYPE:
            return self.create_cloud_event(
                event_id=str(uuid.uuid4()),
                source=SOURCE,
                event_type=CALC_RESP_EVENT_TYPE,
                data={
                    "requestId": data.get('requestId'),
                    "entityId": data.get('entityId'),
                    "owner": OWNER,
                    "payload": data.get('payload'),
                    "success": True
                }
            )
        elif type == CRITERIA_CALC_REQ_EVENT_TYPE:
            return self.create_cloud_event(
                event_id=str(uuid.uuid4()),
                source=SOURCE,
                event_type=CRITERIA_CALC_RESP_EVENT_TYPE,
                data={
                    "requestId": data.get('requestId'),
                    "entityId": data.get('entityId'),
                    "owner": OWNER,
                    "matches": response,
                    "success": True
                }
            )

    async def event_generator(self, queue: asyncio.Queue):
        """
        Generate and yield events including initial and follow-up events.

        :param queue: Async queue to get events from.
        :yield: CloudEvent instances.
        """
        # Yield the initial join event
        yield self.create_join_event()
        while True:
            event = await queue.get()
            if event is None:
                break
            yield event
            queue.task_done()

    # Utility function to set up gRPC credentials
    def get_grpc_credentials(self, token: str):
        """
        Create gRPC credentials using the provided token.

        :param token: Authentication token for the gRPC service.
        :return: Composite credentials for secure gRPC communication.
        """
        auth_creds = grpc.access_token_call_credentials(token)
        return grpc.composite_channel_credentials(grpc.ssl_channel_credentials(), auth_creds)

    # Function to handle greeting response
    def handle_greet_event(self):
        """
        Handle the GREET_EVENT_TYPE response.

        :param response: gRPC response containing the event details.
        """
        logger.info("handle_greet_event:")

    async def handle_keep_alive_event(self, response, queue: asyncio.Queue):
        logger.debug(f"handle_keep_alive_event: {response}")
        data = json.loads(response.text_data)
        event = self.create_cloud_event(
            event_id=str(uuid.uuid4()),
            source=SOURCE,
            event_type=EVENT_ACK_TYPE,
            data={
                "sourceEventId": data.get('id'),
                "owner": OWNER,
                "payload": None,
                "success": True
            })
        await queue.put(event)

    # Function to process notification entity and create the notification event
    async def process_calc_req_event(self, data: dict, queue: asyncio.Queue, type: str):
        """
        Process notification entity and create a notification event to be added to the event queue.

        :param data: The notification entity received from the response.
        :param queue: The asyncio queue for event processing.
        """
        if type == CALC_REQ_EVENT_TYPE:
            processor_name = data.get('processorName')
        elif type == CRITERIA_CALC_REQ_EVENT_TYPE:
            processor_name = data.get('criteriaName')
        else:
            raise Exception(f"Unknown grpc request type: {type}")
        entity_id = data.get('entityId')
        action = {
            "name": processor_name,
            "config": json.loads(data.get('parameters').get('context'))
        }
        model_key_name = data.get('payload').get('meta').get('modelKey').get('name')

        # Retrieve the appropriate model class from the registry.
        # Default to WorkflowEntity if the meta info isn’t recognized.
        model_cls = model_registry.get(model_key_name, WorkflowEntity)

        # Validate the payload data with the chosen model class.
        entity = model_cls.model_validate(data.get('payload').get('data'))
        entity.current_transition = data.get('transition').get('name')
        response = None
        try:
            # Process the first or subsequent versions of the entity
            logger.debug(f"Processing notification entity: {data}")
            entity, response = await self.workflow_dispatcher.process_event(entity=entity,
                                                                            action=action,
                                                                            technical_id=entity_id)
            data['payload']['data'] = model_cls.model_dump(entity)

        except Exception as e:
            logger.exception(e)
        # Create notification event and put it in the queue
        notification_event = self.create_notification_event(data=data, response=response, type=type)
        await queue.put(notification_event)

    # Function to handle finish_workflow processor
    async def handle_finish_workflow(self, data: dict, queue: asyncio.Queue):
        """
        Handle the 'finish_workflow' processorName and signal the end of the stream.

        :param data: Data from the response.
        :param queue: Event queue to place the notification event and signal end of stream.
        """
        notification_event = self.create_notification_event(data=data, type=CALC_REQ_EVENT_TYPE)
        await queue.put(notification_event)
        # await queue.put(None)  # Signal the end of the stream

    # Main function to consume the gRPC stream
    async def consume_stream(self, token):
        """
        Handle bidirectional streaming with response-driven event generation.
        """
        credentials = self.get_grpc_credentials(token)
        queue = asyncio.Queue()

        async with grpc.aio.secure_channel(config.GRPC_ADDRESS, credentials) as channel:
            stub = CloudEventsServiceStub(channel)
            call = stub.startStreaming(self.event_generator(queue))

            async for response in call:
                logger.debug(f"Received response: {response}")

                if response.type == KEEP_ALIVE_EVENT_TYPE:
                    await self.handle_keep_alive_event(response, queue)
                elif response.type == EVENT_ACK_TYPE:
                    logger.debug(response)
                elif response.type == CALC_REQ_EVENT_TYPE or response.type == CRITERIA_CALC_REQ_EVENT_TYPE:
                    logger.info(f"Received calc request: {response}")
                    # Parse response entity
                    data = json.loads(response.text_data)
                    processor_name = data.get('processorName')
                    await self.process_calc_req_event(data=data, queue=queue, type=response.type)
                    if processor_name == "finish_workflow":
                        await self.handle_finish_workflow(data, queue)
                elif response.type == GREET_EVENT_TYPE:
                    self.handle_greet_event()
                else:
                    logger.exception(f"Unsupported grpc request type {response.type}")

    async def grpc_stream(self, token):
        try:
            while True:
                await self.consume_stream(token)
                logger.debug("Working...")
        except asyncio.CancelledError:
            logger.exception("consume_stream was cancelled")
            raise
