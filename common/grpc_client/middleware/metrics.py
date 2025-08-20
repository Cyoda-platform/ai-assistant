from cloudevents_pb2 import CloudEvent

from common.grpc_client.middleware.base import MiddlewareLink


class MetricsMiddleware(MiddlewareLink):
    async def handle(self, event: CloudEvent):
        # placeholder for metrics; no-op to preserve behavior
        return await super().handle(event)

