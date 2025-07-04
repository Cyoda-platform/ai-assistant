import logging
import uuid
import json
import asyncio

import grpc

from cloudevents_pb2 import CloudEvent
from common.config import config
from common.config.config import config
from common.utils.event_loop import BackgroundEventLoop
from cyoda_cloud_api_pb2_grpc import CloudEventsServiceStub
from entity.model import WorkflowEntity
from entity.model_registry import model_registry

# These tags/configs from your original snippet
TAGS = [config.GRPC_PROCESSOR_TAG]
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


logger = logging.getLogger(__name__)


class GrpcClient:
    def __init__(self, workflow_dispatcher, auth, chat_service):
        self.workflow_dispatcher = workflow_dispatcher
        self.auth = auth
        self.chat_service = chat_service
        self.processor_loop = BackgroundEventLoop()

    def metadata_callback(self, context, callback):
        """
        gRPC metadata provider that attaches a fresh Bearer token.
        If retrieving the token fails, it invalidates and retries once.
        """
        try:
            token = self.auth.get_access_token()
        except Exception as e:
            logger.exception(e)
            logger.warning("Access‑token fetch failed, invalidating and retrying", exc_info=e)
            self.auth.invalidate_tokens()
            token = self.auth.get_access_token()

        callback([('authorization', f'Bearer {token}')], None)

    def get_grpc_credentials(self) -> grpc.ChannelCredentials:
        """
        Create composite credentials: SSL + per‑call metadata token.
        """
        call_creds = grpc.metadata_call_credentials(self.metadata_callback)
        ssl_creds = grpc.ssl_channel_credentials()
        return grpc.composite_channel_credentials(ssl_creds, call_creds)

    def create_cloud_event(self, event_id: str, source: str, event_type: str, data: dict) -> CloudEvent:
        return CloudEvent(
            id=event_id,
            source=source,
            spec_version=SPEC_VERSION,
            type=event_type,
            text_data=json.dumps(data),
        )

    def create_join_event(self) -> CloudEvent:
        return self.create_cloud_event(
            event_id=str(uuid.uuid4()),
            source=SOURCE,
            event_type=JOIN_EVENT_TYPE,
            data={"owner": OWNER, "tags": TAGS},
        )

    def create_notification_event(self, data: dict, type: str, response=None) -> CloudEvent:
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
        else:
            raise ValueError(f"Unsupported notification type: {type}")

    async def event_generator(self, queue: asyncio.Queue):
        yield self.create_join_event()
        while True:
            event = await queue.get()
            if event is None:
                break
            yield event
            logger.info(f"event done {event.id} {event.type}")
            queue.task_done()

    async def handle_keep_alive_event(self, response, queue: asyncio.Queue):
        data = json.loads(response.text_data)
        ack = self.create_cloud_event(
            event_id=str(uuid.uuid4()),
            source=SOURCE,
            event_type=EVENT_ACK_TYPE,
            data={
                "sourceEventId": data.get('id'),
                "owner": OWNER,
                "payload": None,
                "success": True,
            },
        )
        logger.info(f"ack_keep_alive {data.get('id')}")
        await queue.put(ack)

    async def process_calc_req_event(self, data: dict, queue: asyncio.Queue, type: str):
        if type == CALC_REQ_EVENT_TYPE:
            processor_name = data.get('processorName')
        elif type == CRITERIA_CALC_REQ_EVENT_TYPE:
            processor_name = data.get('criteriaName')
        else:
            raise Exception(f"Unknown grpc request type: {type}")

        model_key = data['payload']['meta']['modelKey']['name']
        model_cls = model_registry.get(model_key, WorkflowEntity)

        entity = model_cls.model_validate(data['payload']['data'])
        entity.current_transition = data['transition']['name']

        try:
            entity, resp = await self.workflow_dispatcher.process_event(
                entity=entity,
                action={
                    "name": processor_name,
                    "config": json.loads(data['parameters']['context'])
                },
                technical_id=data['entityId'])
            data['payload']['data'] = model_cls.model_dump(entity)
        except Exception as e:
            logger.exception("Error processing entity")
            logger.exception(e)
            entity.failed = True
            data['payload']['data'] = model_cls.model_dump(entity)
            resp = None
        logger.info(f"Calc response: processor_name: {processor_name},technical_id={data['entityId']}")
        notif = self.create_notification_event(data=data, response=resp, type=type)
        await queue.put(notif)

    async def consume_stream(self):
        backoff = 1
        while True:
            creds = self.get_grpc_credentials()
            queue = asyncio.Queue()

            try:
                # 1) Define keep-alive options (milliseconds unless noted)
                keepalive_opts = [
                    ('grpc.keepalive_time_ms', 15_000),  # PING every 30 s
                    ('grpc.keepalive_timeout_ms', 30_000),  # wait 10 s for PONG
                    ('grpc.keepalive_permit_without_calls', 1),  # even if idle
                    ('grpc.enable_http_proxy', 0)
                ]

                # 2) Pass them into secure_channel alongside your creds
                async with grpc.aio.secure_channel(
                        config.GRPC_ADDRESS,
                        creds,
                        options=keepalive_opts
                ) as channel:
                    stub = CloudEventsServiceStub(channel)
                    call = stub.startStreaming(self.event_generator(queue))
                    # … then await call or iterate its stream as needed

                    async for response in call:
                        if response.type == KEEP_ALIVE_EVENT_TYPE:
                            asyncio.create_task(self.handle_keep_alive_event(response, queue))
                        elif response.type == EVENT_ACK_TYPE:
                            logger.debug(response)
                        elif response.type in (CALC_REQ_EVENT_TYPE, CRITERIA_CALC_REQ_EVENT_TYPE):
                            logger.info(f"Calc request: {response.type}")
                            data = json.loads(response.text_data)
                            asyncio.create_task(self.process_calc_req_event(data, queue, response.type))
                        elif response.type == GREET_EVENT_TYPE:
                            logger.info("Greet event received")
                            self.processor_loop.run_coroutine(self.rollback_failed_workflows())
                        else:
                            logger.error(f"Unhandled event type: {response.type}")

                # If we exit the stream cleanly, break out of the retry loop
                logger.info("Stream closed by server—reconnecting")
                backoff = 1  # reset your backoff if you like
                continue

            except grpc.RpcError as e:
                logger.exception(e)
                # UNAUTHENTICATED → invalidate tokens, then retry with fresh creds
                if getattr(e, "code", lambda: None)() == grpc.StatusCode.UNAUTHENTICATED:
                    logger.warning(
                        "Stream got UNAUTHENTICATED—invalidating tokens and retrying",
                        exc_info=e,
                    )
                    self.auth.invalidate_tokens()
                else:
                    # Log everything else and retry
                    logger.exception("gRPC RpcError in consume_stream", exc_info=e)


            except Exception as e:
                # Catch-all for anything unexpected
                logger.exception(e)
                logger.exception("Unexpected error in consume_stream", exc_info=e)

            # back off and retry
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)  # exponential backoff up to 30s

    async def grpc_stream(self):
        """
        Entry point: keeps the bidirectional stream alive, reconnecting on token revocations.
        """
        try:
            await self.consume_stream()
        except Exception as e:
            logger.exception(e)


    async def rollback_failed_workflows(self):
        logger.info("restarting entities workflows....")
        try:
            asyncio.create_task(self.chat_service.rollback_failed_workflows())
        except Exception as e:
            logger.error("Failed to restart entities")
            logger.exception(e)
