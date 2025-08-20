import logging

from cloudevents_pb2 import CloudEvent

from common.grpc_client.middleware.base import MiddlewareLink

logger = logging.getLogger(__name__)


class ErrorMiddleware(MiddlewareLink):
    async def handle(self, event: CloudEvent):
        try:
            return await super().handle(event)
        except Exception as e:
            # per user request: always log with logger.exception
            logger.exception("Unhandled exception while processing event", exc_info=e)
            # preserve current behavior: do not emit error responses
            return None

