"""
Comprehensive tests for gRPC client components with high test coverage.
"""
import asyncio
import json
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cloudevents_pb2 import CloudEvent

from common.grpc_client.constants import (
    CALC_REQ_EVENT_TYPE, CRITERIA_CALC_REQ_EVENT_TYPE, KEEP_ALIVE_EVENT_TYPE, EVENT_ACK_TYPE,
    GREET_EVENT_TYPE, ERROR_EVENT_TYPE, JOIN_EVENT_TYPE, CALC_RESP_EVENT_TYPE, CRITERIA_CALC_RESP_EVENT_TYPE
)
from common.grpc_client.router import EventRouter
from common.grpc_client.responses.builders import (
    ResponseBuilderRegistry, JoinResponseBuilder, AckResponseBuilder,
    CalcResponseBuilder, CriteriaCalcResponseBuilder
)
from common.grpc_client.responses.spec import ResponseSpec
from common.grpc_client.outbox import Outbox
from common.grpc_client.middleware.dispatch import DispatchMiddleware
from common.grpc_client.middleware.logging import LoggingMiddleware
from common.grpc_client.middleware.metrics import MetricsMiddleware
from common.grpc_client.middleware.error import ErrorMiddleware
from common.grpc_client.handlers.keep_alive import KeepAliveHandler
from common.grpc_client.handlers.ack import AckHandler
from common.grpc_client.handlers.greet import GreetHandler
from common.grpc_client.handlers.error import ErrorHandler
from common.grpc_client.handlers.calc import CalcRequestHandler
from common.grpc_client.handlers.criteria_calc import CriteriaCalcRequestHandler
from common.grpc_client.factory import GrpcStreamingFacadeFactory
import entity.model_registry as mr


class DummyDispatcher:
    async def process_event(self, *, entity, processor_name, payload, technical_id):
        return entity, payload.get("payload")


class FailingDispatcher:
    async def process_event(self, *, entity, processor_name, payload, technical_id):
        raise Exception("Processing failed")


class DummyModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.failed = False
        self.current_transition = None

    @staticmethod
    def model_validate(d):
        return DummyModel(**d)

    @staticmethod
    def model_dump(obj):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}


@pytest.fixture
def mock_model_registry(monkeypatch):
    """Mock the model registry for tests."""
    monkeypatch.setitem(mr.model_registry, "CHAT_ENTITY", DummyModel)


# ============= EventRouter Tests =============

def test_event_router_register_and_route():
    """Test EventRouter registration and routing."""
    router = EventRouter()
    handler = KeepAliveHandler()

    # Test registration
    router.register(KEEP_ALIVE_EVENT_TYPE, handler)

    # Test routing
    event = types.SimpleNamespace(type=KEEP_ALIVE_EVENT_TYPE)
    routed_handler = router.route(event)
    assert routed_handler is handler

    # Test unknown event type
    unknown_event = types.SimpleNamespace(type="UnknownEventType")
    assert router.route(unknown_event) is None


# ============= ResponseBuilder Tests =============

def test_join_response_builder():
    """Test JoinResponseBuilder."""
    builder = JoinResponseBuilder()
    spec = ResponseSpec(response_type=JOIN_EVENT_TYPE, data={})

    response = builder.build(spec)

    assert response.type == JOIN_EVENT_TYPE
    assert response.source == "SimpleSample"  # This is the actual source from constants
    assert response.spec_version == "1.0"

    data = json.loads(response.text_data)
    assert "id" in data
    assert data["owner"] == "PLAY"  # This is the actual OWNER from constants
    assert data["tags"] == ["ai_assistant"]  # This comes from config.GRPC_PROCESSOR_TAG


def test_ack_response_builder():
    """Test AckResponseBuilder."""
    builder = AckResponseBuilder()
    spec = ResponseSpec(
        response_type=EVENT_ACK_TYPE,
        data={},
        source_event_id="source123",
        success=True
    )

    response = builder.build(spec)

    assert response.type == EVENT_ACK_TYPE
    data = json.loads(response.text_data)
    assert data["sourceEventId"] == "source123"
    assert data["success"] is True


def test_calc_response_builder():
    """Test CalcResponseBuilder."""
    builder = CalcResponseBuilder()
    spec = ResponseSpec(
        response_type=CALC_RESP_EVENT_TYPE,
        data={
            "requestId": "req1",
            "entityId": "ent1",
            "payload": {"test": "data"}
        },
        success=True
    )

    response = builder.build(spec)

    assert response.type == CALC_RESP_EVENT_TYPE
    data = json.loads(response.text_data)
    assert data["requestId"] == "req1"
    assert data["entityId"] == "ent1"
    assert data["success"] is True
    assert data["payload"] == {"test": "data"}


def test_criteria_calc_response_builder():
    """Test CriteriaCalcResponseBuilder."""
    builder = CriteriaCalcResponseBuilder()
    spec = ResponseSpec(
        response_type=CRITERIA_CALC_RESP_EVENT_TYPE,
        data={
            "requestId": "req1",
            "entityId": "ent1",
            "matches": ["match1", "match2"]
        },
        success=True
    )

    response = builder.build(spec)

    assert response.type == CRITERIA_CALC_RESP_EVENT_TYPE
    data = json.loads(response.text_data)
    assert data["matches"] == ["match1", "match2"]


def test_response_builder_registry():
    """Test ResponseBuilderRegistry."""
    registry = ResponseBuilderRegistry()
    builder = JoinResponseBuilder()

    # Test registration
    registry.register(JOIN_EVENT_TYPE, builder)

    # Test retrieval
    retrieved = registry.get(JOIN_EVENT_TYPE)
    assert retrieved is builder

    # Test unknown type
    with pytest.raises(KeyError, match="No builder registered"):
        registry.get("UnknownType")


# ============= Handler Tests =============

@pytest.mark.asyncio
async def test_keep_alive_handler():
    """Test KeepAliveHandler."""
    handler = KeepAliveHandler()
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=KEEP_ALIVE_EVENT_TYPE,
        text_data=json.dumps({"id": "keepalive123"})
    )

    spec = await handler.handle(event)

    assert spec.response_type == EVENT_ACK_TYPE
    assert spec.source_event_id == "keepalive123"
    assert spec.success is True


@pytest.mark.asyncio
async def test_ack_handler():
    """Test AckHandler."""
    handler = AckHandler()
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=EVENT_ACK_TYPE,
        text_data=json.dumps({"sourceEventId": "source123"})
    )

    spec = await handler.handle(event)
    assert spec is None  # AckHandler returns None


@pytest.mark.asyncio
async def test_greet_handler():
    """Test GreetHandler."""
    handler = GreetHandler()
    mock_chat_service = AsyncMock()
    mock_processor_loop = MagicMock()

    services = types.SimpleNamespace(
        chat_service=mock_chat_service,
        processor_loop=mock_processor_loop
    )

    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=GREET_EVENT_TYPE,
        text_data=json.dumps({"message": "hello"})
    )

    spec = await handler.handle(event, services)

    assert spec is None
    mock_processor_loop.run_coroutine.assert_called_once()


@pytest.mark.asyncio
async def test_error_handler():
    """Test ErrorHandler."""
    handler = ErrorHandler()
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=ERROR_EVENT_TYPE,
        text_data=json.dumps({
            "code": "TEST_ERROR",
            "message": "Test error message",
            "sourceEventId": "source123"
        })
    )

    spec = await handler.handle(event)
    assert spec is None  # ErrorHandler returns None


@pytest.mark.asyncio
async def test_calc_request_handler_success(mock_model_registry):
    """Test CalcRequestHandler success case."""
    handler = CalcRequestHandler()
    dispatcher = DummyDispatcher()
    services = types.SimpleNamespace(workflow_dispatcher=dispatcher)

    payload = {
        "entityId": "e1",
        "requestId": "r1",
        "processorName": "p1",
        "payload": {"meta": {"modelKey": {"name": "CHAT_ENTITY"}}, "data": {"id": "e1"}},
        "transition": {"name": "t1"},
    }
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=CALC_REQ_EVENT_TYPE,
        text_data=json.dumps(payload)
    )

    spec = await handler.handle(event, services)

    assert spec.response_type == CALC_RESP_EVENT_TYPE
    assert spec.data["entityId"] == "e1"
    assert spec.data["requestId"] == "r1"
    assert spec.success is True


@pytest.mark.asyncio
async def test_calc_request_handler_failure(mock_model_registry):
    """Test CalcRequestHandler failure case."""
    handler = CalcRequestHandler()
    dispatcher = FailingDispatcher()
    services = types.SimpleNamespace(workflow_dispatcher=dispatcher)

    payload = {
        "entityId": "e1",
        "requestId": "r1",
        "processorName": "p1",
        "payload": {"meta": {"modelKey": {"name": "CHAT_ENTITY"}}, "data": {"id": "e1"}},
        "transition": {"name": "t1"},
    }
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=CALC_REQ_EVENT_TYPE,
        text_data=json.dumps(payload)
    )

    spec = await handler.handle(event, services)

    # Should still return success=True even on failure
    assert spec.response_type == CALC_RESP_EVENT_TYPE
    assert spec.success is True


@pytest.mark.asyncio
async def test_criteria_calc_request_handler_success(mock_model_registry):
    """Test CriteriaCalcRequestHandler success case."""
    handler = CriteriaCalcRequestHandler()
    dispatcher = DummyDispatcher()
    services = types.SimpleNamespace(workflow_dispatcher=dispatcher)

    payload = {
        "entityId": "e1",
        "requestId": "r1",
        "criteriaName": "c1",
        "payload": {"meta": {"modelKey": {"name": "CHAT_ENTITY"}}, "data": {"id": "e1"}},
        "transition": {"name": "t1"},
    }
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=CRITERIA_CALC_REQ_EVENT_TYPE,
        text_data=json.dumps(payload)
    )

    spec = await handler.handle(event, services)

    assert spec.response_type == CRITERIA_CALC_RESP_EVENT_TYPE
    assert spec.data["entityId"] == "e1"
    assert spec.data["requestId"] == "r1"
    assert spec.success is True


@pytest.mark.asyncio
async def test_calc_handler_missing_services(mock_model_registry):
    """Test CalcRequestHandler with missing services."""
    handler = CalcRequestHandler()

    payload = {
        "entityId": "e1",
        "requestId": "r1",
        "processorName": "p1",
        "payload": {"meta": {"modelKey": {"name": "CHAT_ENTITY"}}, "data": {"id": "e1"}},
        "transition": {"name": "t1"},
    }
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=CALC_REQ_EVENT_TYPE,
        text_data=json.dumps(payload)
    )

    spec = await handler.handle(event, services=None)

    # Should still return success=True even when services are missing
    assert spec.response_type == CALC_RESP_EVENT_TYPE
    assert spec.success is True

# ============= Middleware Tests =============

@pytest.mark.asyncio
async def test_logging_middleware():
    """Test LoggingMiddleware."""
    middleware = LoggingMiddleware()
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=KEEP_ALIVE_EVENT_TYPE,
        text_data=json.dumps({"id": "test"})
    )

    # Should not raise exception and pass to successor
    result = await middleware.handle(event)
    assert result is None


@pytest.mark.asyncio
async def test_metrics_middleware():
    """Test MetricsMiddleware."""
    middleware = MetricsMiddleware()
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=KEEP_ALIVE_EVENT_TYPE,
        text_data=json.dumps({"id": "test"})
    )

    # Should not raise exception and pass to successor
    result = await middleware.handle(event)
    assert result is None


@pytest.mark.asyncio
async def test_error_middleware():
    """Test ErrorMiddleware exception handling."""
    # Create a failing successor
    class FailingMiddleware:
        async def handle(self, event):
            raise Exception("Test exception")

    middleware = ErrorMiddleware()
    middleware.set_successor(FailingMiddleware())

    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=KEEP_ALIVE_EVENT_TYPE,
        text_data=json.dumps({"id": "test"})
    )

    # Should catch exception and not re-raise
    result = await middleware.handle(event)
    assert result is None


@pytest.mark.asyncio
async def test_dispatch_middleware_success(mock_model_registry):
    """Test DispatchMiddleware successful dispatch."""
    router = EventRouter()
    builders = ResponseBuilderRegistry()
    outbox = Outbox()

    router.register(KEEP_ALIVE_EVENT_TYPE, KeepAliveHandler())
    builders.register(EVENT_ACK_TYPE, AckResponseBuilder())

    middleware = DispatchMiddleware(router, builders, outbox, services=None)

    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=KEEP_ALIVE_EVENT_TYPE,
        text_data=json.dumps({"id": "keepalive123"})
    )

    await middleware.handle(event)

    # Check that response was queued
    response = await outbox._queue.get()
    assert response.type == EVENT_ACK_TYPE


@pytest.mark.asyncio
async def test_dispatch_middleware_unhandled_event():
    """Test DispatchMiddleware with unhandled event type."""
    router = EventRouter()
    builders = ResponseBuilderRegistry()
    outbox = Outbox()

    middleware = DispatchMiddleware(router, builders, outbox, services=None)

    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type="UnknownEventType",
        text_data=json.dumps({"id": "test"})
    )

    result = await middleware.handle(event)
    assert result is None

    # Queue should be empty
    assert outbox._queue.empty()


@pytest.mark.asyncio
async def test_dispatch_middleware_handler_returns_none():
    """Test DispatchMiddleware when handler returns None."""
    router = EventRouter()
    builders = ResponseBuilderRegistry()
    outbox = Outbox()

    router.register(EVENT_ACK_TYPE, AckHandler())  # AckHandler returns None

    middleware = DispatchMiddleware(router, builders, outbox, services=None)

    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=EVENT_ACK_TYPE,
        text_data=json.dumps({"sourceEventId": "test"})
    )

    result = await middleware.handle(event)
    assert result is None

    # Queue should be empty since handler returned None
    assert outbox._queue.empty()


# ============= Middleware Chain Tests =============

@pytest.mark.asyncio
async def test_middleware_chain(mock_model_registry):
    """Test complete middleware chain."""
    router = EventRouter()
    builders = ResponseBuilderRegistry()
    outbox = Outbox()

    router.register(KEEP_ALIVE_EVENT_TYPE, KeepAliveHandler())
    builders.register(EVENT_ACK_TYPE, AckResponseBuilder())

    # Create middleware chain
    logging_middleware = LoggingMiddleware()
    metrics_middleware = MetricsMiddleware()
    error_middleware = ErrorMiddleware()
    dispatch_middleware = DispatchMiddleware(router, builders, outbox, services=None)

    # Chain them together
    logging_middleware.set_successor(metrics_middleware)
    metrics_middleware.set_successor(error_middleware)
    error_middleware.set_successor(dispatch_middleware)

    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=KEEP_ALIVE_EVENT_TYPE,
        text_data=json.dumps({"id": "keepalive123"})
    )

    await logging_middleware.handle(event)

    # Check that response was processed through the entire chain
    response = await outbox._queue.get()
    assert response.type == EVENT_ACK_TYPE

# ============= Outbox Tests =============

@pytest.mark.asyncio
async def test_outbox_send_and_event_generator():
    """Test Outbox send and event_generator."""
    outbox = Outbox()

    # Create a test response
    test_response = CloudEvent(
        id="test_resp", source="test", spec_version="1.0", type=EVENT_ACK_TYPE,
        text_data=json.dumps({"test": "response"})
    )

    # Send response
    await outbox.send(test_response)
    await outbox.close()  # Send sentinel

    # Collect events from generator
    events = []
    async for event in outbox.event_generator():
        events.append(event)

    # Should have join event first, then test response
    assert len(events) == 2
    assert events[0].type == JOIN_EVENT_TYPE
    assert events[1].type == EVENT_ACK_TYPE


@pytest.mark.asyncio
async def test_outbox_close():
    """Test Outbox close functionality."""
    outbox = Outbox()

    await outbox.close()

    # Should be able to get the sentinel
    sentinel = await outbox._queue.get()
    assert sentinel is None


# ============= Factory Tests =============

def test_grpc_streaming_facade_factory():
    """Test GrpcStreamingFacadeFactory."""
    mock_dispatcher = DummyDispatcher()
    mock_auth = MagicMock()
    mock_chat_service = AsyncMock()
    mock_processor_loop = MagicMock()

    facade = GrpcStreamingFacadeFactory.create(
        workflow_dispatcher=mock_dispatcher,
        auth=mock_auth,
        chat_service=mock_chat_service,
        processor_loop=mock_processor_loop
    )

    # Verify facade is created with all components
    assert facade is not None
    assert facade.router is not None
    assert facade.builders is not None
    assert facade.outbox is not None
    assert facade.first_middleware is not None

    # Verify handlers are registered
    keep_alive_event = types.SimpleNamespace(type=KEEP_ALIVE_EVENT_TYPE)
    handler = facade.router.route(keep_alive_event)
    assert handler is not None

    # Verify builders are registered
    ack_builder = facade.builders.get(EVENT_ACK_TYPE)
    assert ack_builder is not None


# ============= Integration Tests =============

@pytest.mark.asyncio
async def test_full_integration_calc_request(mock_model_registry):
    """Test full integration from event to response."""
    mock_dispatcher = DummyDispatcher()
    mock_auth = MagicMock()
    mock_chat_service = AsyncMock()
    mock_processor_loop = MagicMock()

    # Create facade using factory
    facade = GrpcStreamingFacadeFactory.create(
        workflow_dispatcher=mock_dispatcher,
        auth=mock_auth,
        chat_service=mock_chat_service,
        processor_loop=mock_processor_loop
    )

    # Create calc request event
    payload = {
        "entityId": "e1",
        "requestId": "r1",
        "processorName": "p1",
        "payload": {"meta": {"modelKey": {"name": "CHAT_ENTITY"}}, "data": {"id": "e1"}},
        "transition": {"name": "t1"},
    }
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=CALC_REQ_EVENT_TYPE,
        text_data=json.dumps(payload)
    )

    # Process event through middleware chain
    await facade.first_middleware.handle(event)

    # Check response was generated
    response = await facade.outbox._queue.get()
    assert response.type == CALC_RESP_EVENT_TYPE

    response_data = json.loads(response.text_data)
    assert response_data["entityId"] == "e1"
    assert response_data["requestId"] == "r1"
    assert response_data["success"] is True


@pytest.mark.asyncio
async def test_full_integration_keep_alive(mock_model_registry):
    """Test full integration for keep alive event."""
    mock_dispatcher = DummyDispatcher()
    mock_auth = MagicMock()
    mock_chat_service = AsyncMock()
    mock_processor_loop = MagicMock()

    # Create facade using factory
    facade = GrpcStreamingFacadeFactory.create(
        workflow_dispatcher=mock_dispatcher,
        auth=mock_auth,
        chat_service=mock_chat_service,
        processor_loop=mock_processor_loop
    )

    # Create keep alive event
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=KEEP_ALIVE_EVENT_TYPE,
        text_data=json.dumps({"id": "keepalive123"})
    )

    # Process event through middleware chain
    await facade.first_middleware.handle(event)

    # Check ACK response was generated
    response = await facade.outbox._queue.get()
    assert response.type == EVENT_ACK_TYPE

    response_data = json.loads(response.text_data)
    assert response_data["sourceEventId"] == "keepalive123"
    assert response_data["success"] is True


@pytest.mark.asyncio
async def test_full_integration_greet_event(mock_model_registry):
    """Test full integration for greet event."""
    mock_dispatcher = DummyDispatcher()
    mock_auth = MagicMock()
    mock_chat_service = AsyncMock()
    mock_processor_loop = MagicMock()

    # Create facade using factory
    facade = GrpcStreamingFacadeFactory.create(
        workflow_dispatcher=mock_dispatcher,
        auth=mock_auth,
        chat_service=mock_chat_service,
        processor_loop=mock_processor_loop
    )

    # Create greet event
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=GREET_EVENT_TYPE,
        text_data=json.dumps({"message": "hello"})
    )

    # Process event through middleware chain
    await facade.first_middleware.handle(event)

    # Check that rollback was triggered
    mock_processor_loop.run_coroutine.assert_called_once()

    # Queue should be empty since greet handler returns None
    assert facade.outbox._queue.empty()


# ============= Error Handling Tests =============

@pytest.mark.asyncio
async def test_error_handling_in_middleware_chain(mock_model_registry):
    """Test error handling throughout the middleware chain."""
    # Create a dispatcher that fails
    failing_dispatcher = FailingDispatcher()
    mock_auth = MagicMock()
    mock_chat_service = AsyncMock()
    mock_processor_loop = MagicMock()

    # Create facade with failing dispatcher
    facade = GrpcStreamingFacadeFactory.create(
        workflow_dispatcher=failing_dispatcher,
        auth=mock_auth,
        chat_service=mock_chat_service,
        processor_loop=mock_processor_loop
    )

    # Create calc request event
    payload = {
        "entityId": "e1",
        "requestId": "r1",
        "processorName": "p1",
        "payload": {"meta": {"modelKey": {"name": "CHAT_ENTITY"}}, "data": {"id": "e1"}},
        "transition": {"name": "t1"},
    }
    event = CloudEvent(
        id="test", source="test", spec_version="1.0", type=CALC_REQ_EVENT_TYPE,
        text_data=json.dumps(payload)
    )

    # Process event - should not raise exception due to error middleware
    await facade.first_middleware.handle(event)

    # Should still get a response with success=True
    response = await facade.outbox._queue.get()
    assert response.type == CALC_RESP_EVENT_TYPE

    response_data = json.loads(response.text_data)
    assert response_data["success"] is True  # Always true even on failure