"""
Simple, dull GrpcClient for backward compatibility.
All complex logic has been moved to factory.py and legacy_methods.py.
"""
import logging
import asyncio

import grpc
from cloudevents_pb2 import CloudEvent
from common.utils.event_loop import BackgroundEventLoop

# Import constants for backward compatibility
from common.grpc_client.constants import (
    TAGS, OWNER, SPEC_VERSION, SOURCE,
    JOIN_EVENT_TYPE, CALC_RESP_EVENT_TYPE, CALC_REQ_EVENT_TYPE,
    CRITERIA_CALC_REQ_EVENT_TYPE, CRITERIA_CALC_RESP_EVENT_TYPE,
    GREET_EVENT_TYPE, KEEP_ALIVE_EVENT_TYPE, EVENT_ACK_TYPE, ERROR_EVENT_TYPE,
)

logger = logging.getLogger(__name__)


class GrpcClient:
    """
    Dull wrapper class for backward compatibility.
    All logic moved elsewhere - this just delegates.
    """
    def __init__(self, workflow_dispatcher, auth, chat_service):
        # Store dependencies
        self.workflow_dispatcher = workflow_dispatcher
        self.auth = auth
        self.chat_service = chat_service
        self.processor_loop = BackgroundEventLoop()

        # Lazy initialization
        self._facade = None

    def _get_facade(self):
        """Get facade, creating it if needed."""
        if self._facade is None:
            from common.grpc_client.factory import GrpcStreamingFacadeFactory
            self._facade = GrpcStreamingFacadeFactory.create(
                workflow_dispatcher=self.workflow_dispatcher,
                auth=self.auth,
                chat_service=self.chat_service,
                processor_loop=self.processor_loop,
                grpc_client=self
            )
        return self._facade

    # Properties for backward compatibility
    @property
    def router(self):
        return self._get_facade().router

    @property
    def builders(self):
        return self._get_facade().builders

    @property
    def outbox(self):
        return self._get_facade().outbox

    @property
    def middleware(self):
        return self._get_facade().first_middleware

    @property
    def facade(self):
        return self._get_facade()

    @property
    def _queue(self):
        return self._get_facade().outbox._queue

    # Auth methods - minimal logic
    def metadata_callback(self, context, callback):
        """gRPC metadata provider."""
        try:
            token = self.auth.get_access_token()
        except Exception as e:
            logger.exception(e)
            logger.warning("Access‑token fetch failed, invalidating and retrying", exc_info=e)
            self.auth.invalidate_tokens()
            token = self.auth.get_access_token()
        callback([('authorization', f'Bearer {token}')], None)

    def get_grpc_credentials(self) -> grpc.ChannelCredentials:
        """Create composite credentials."""
        call_creds = grpc.metadata_call_credentials(self.metadata_callback)
        ssl_creds = grpc.ssl_channel_credentials()
        return grpc.composite_channel_credentials(ssl_creds, call_creds)

    # Main entry points - simple delegation
    async def grpc_stream(self):
        """Entry point."""
        try:
            await self._get_facade().start()
        except Exception as e:
            logger.exception(e)

    async def start(self):
        return await self._get_facade().start()

    def stop(self):
        return self._get_facade().stop()

    def _on_event(self, event: CloudEvent):
        return self._get_facade()._on_event(event)

    async def consume_stream(self):
        return await self._get_facade()._consume_stream()




# Re-export constants for backward compatibility
__all__ = [
    'GrpcClient', 'TAGS', 'OWNER', 'SPEC_VERSION', 'SOURCE',
    'JOIN_EVENT_TYPE', 'CALC_RESP_EVENT_TYPE', 'CALC_REQ_EVENT_TYPE',
    'CRITERIA_CALC_REQ_EVENT_TYPE', 'CRITERIA_CALC_RESP_EVENT_TYPE',
    'GREET_EVENT_TYPE', 'KEEP_ALIVE_EVENT_TYPE', 'EVENT_ACK_TYPE', 'ERROR_EVENT_TYPE'
]
