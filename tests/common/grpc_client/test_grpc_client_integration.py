"""
Comprehensive integration tests for GrpcClient with high test coverage.
"""
import asyncio
import json
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cloudevents_pb2 import CloudEvent
from common.grpc_client.grpc_client import GrpcClient
from common.grpc_client.constants import (
    CALC_REQ_EVENT_TYPE, CRITERIA_CALC_REQ_EVENT_TYPE, KEEP_ALIVE_EVENT_TYPE,
    EVENT_ACK_TYPE, GREET_EVENT_TYPE, ERROR_EVENT_TYPE, JOIN_EVENT_TYPE, CALC_RESP_EVENT_TYPE
)
import entity.model_registry as mr


class MockWorkflowDispatcher:
    async def process_event(self, *, entity, processor_name, payload, technical_id):
        entity.processed = True
        return entity, {"result": "success"}


class FailingWorkflowDispatcher:
    async def process_event(self, *, entity, processor_name, payload, technical_id):
        raise Exception("Processing failed")


class MockAuth:
    def __init__(self, should_fail_first=False):
        self.should_fail_first = should_fail_first
        self.call_count = 0

    def get_access_token(self):
        self.call_count += 1
        if self.should_fail_first and self.call_count == 1:
            raise Exception("Token fetch failed")
        return "mock_token"

    def invalidate_tokens(self):
        pass


class MockChatService:
    async def rollback_failed_workflows(self):
        pass


class DummyModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.processed = False
        self.failed = False
        self.current_transition = None

    @staticmethod
    def model_validate(d):
        return DummyModel(**d)

    @staticmethod
    def model_dump(obj):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}


@pytest.fixture
def mock_dependencies(monkeypatch):
    """Mock all external dependencies for GrpcClient."""
    monkeypatch.setitem(mr.model_registry, "CHAT_ENTITY", DummyModel)

    mock_loop = MagicMock()
    mock_loop.run_coroutine = MagicMock()

    with patch('common.grpc_client.grpc_client.BackgroundEventLoop', return_value=mock_loop):
        yield mock_loop


# ============= GrpcClient Initialization Tests =============

def test_grpc_client_initialization():
    """Test GrpcClient initialization."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    # Verify dependencies are stored
    assert client.workflow_dispatcher is dispatcher
    assert client.auth is auth
    assert client.chat_service is chat_service
    assert client.processor_loop is not None

    # Verify facade is not created until accessed
    assert client._facade is None


def test_grpc_client_lazy_facade_creation():
    """Test that facade is created lazily."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    # Facade should be None initially
    assert client._facade is None

    # Accessing facade should create it
    facade = client.facade
    assert facade is not None
    assert client._facade is facade

    # Second access should return same instance
    facade2 = client.facade
    assert facade2 is facade


def test_grpc_client_properties():
    """Test GrpcClient properties."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    # Test all properties
    assert client.router is not None
    assert client.builders is not None
    assert client.outbox is not None
    assert client.middleware is not None
    assert client._queue is not None


# ============= Authentication Tests =============

def test_metadata_callback_success():
    """Test metadata_callback with successful token fetch."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    context = MagicMock()
    callback = MagicMock()

    client.metadata_callback(context, callback)

    callback.assert_called_once_with([('authorization', 'Bearer mock_token')], None)


def test_metadata_callback_with_retry():
    """Test metadata_callback with token fetch failure and retry."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth(should_fail_first=True)
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    context = MagicMock()
    callback = MagicMock()

    client.metadata_callback(context, callback)

    # Should have been called twice (first failed, second succeeded)
    assert auth.call_count == 2
    callback.assert_called_once_with([('authorization', 'Bearer mock_token')], None)


def test_get_grpc_credentials():
    """Test get_grpc_credentials method."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    with patch('common.grpc_client.grpc_client.grpc') as mock_grpc:
        mock_grpc.metadata_call_credentials.return_value = "call_creds"
        mock_grpc.ssl_channel_credentials.return_value = "ssl_creds"
        mock_grpc.composite_channel_credentials.return_value = "composite_creds"

        creds = client.get_grpc_credentials()

        assert creds == "composite_creds"
        mock_grpc.metadata_call_credentials.assert_called_once()
        mock_grpc.ssl_channel_credentials.assert_called_once()
        mock_grpc.composite_channel_credentials.assert_called_once_with("ssl_creds", "call_creds")


# ============= Event Processing Tests =============

@pytest.mark.asyncio
async def test_keep_alive_event_processing(mock_dependencies):
    """Test KeepAlive event processing."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    keepalive_event = CloudEvent(
        id="test_id",
        source="test",
        spec_version="1.0",
        type=KEEP_ALIVE_EVENT_TYPE,
        text_data=json.dumps({"id": "keepalive_123"})
    )

    await client.middleware.handle(keepalive_event)

    response = await client._queue.get()
    assert response.type == EVENT_ACK_TYPE

    response_data = json.loads(response.text_data)
    assert response_data["sourceEventId"] == "keepalive_123"
    assert response_data["success"] is True


@pytest.mark.asyncio
async def test_calc_request_processing_success(mock_dependencies):
    """Test successful calc request processing."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    payload = {
        "entityId": "e1",
        "requestId": "r1",
        "processorName": "test_processor",
        "payload": {
            "meta": {"modelKey": {"name": "CHAT_ENTITY"}},
            "data": {"id": "e1", "name": "test"}
        },
        "transition": {"name": "test_transition"}
    }

    calc_event = CloudEvent(
        id="calc_id",
        source="test",
        spec_version="1.0",
        type=CALC_REQ_EVENT_TYPE,
        text_data=json.dumps(payload)
    )

    await client.middleware.handle(calc_event)

    response = await client._queue.get()
    assert response.type == "EntityProcessorCalculationResponse"

    response_data = json.loads(response.text_data)
    assert response_data["success"] is True
    assert response_data["entityId"] == "e1"
    assert response_data["requestId"] == "r1"


@pytest.mark.asyncio
async def test_calc_request_processing_failure(mock_dependencies):
    """Test calc request processing with failure still returns success=True."""
    dispatcher = FailingWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    payload = {
        "entityId": "e1",
        "requestId": "r1",
        "processorName": "test_processor",
        "payload": {
            "meta": {"modelKey": {"name": "CHAT_ENTITY"}},
            "data": {"id": "e1", "name": "test"}
        },
        "transition": {"name": "test_transition"}
    }

    calc_event = CloudEvent(
        id="calc_id",
        source="test",
        spec_version="1.0",
        type=CALC_REQ_EVENT_TYPE,
        text_data=json.dumps(payload)
    )

    await client.middleware.handle(calc_event)

    response = await client._queue.get()
    assert response.type == "EntityProcessorCalculationResponse"

    response_data = json.loads(response.text_data)
    assert response_data["success"] is True  # Always True per requirements


@pytest.mark.asyncio
async def test_criteria_calc_request_processing(mock_dependencies):
    """Test criteria calc request processing."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    payload = {
        "entityId": "e1",
        "requestId": "r1",
        "criteriaName": "test_criteria",
        "payload": {
            "meta": {"modelKey": {"name": "CHAT_ENTITY"}},
            "data": {"id": "e1", "name": "test"}
        },
        "transition": {"name": "test_transition"}
    }

    criteria_event = CloudEvent(
        id="criteria_id",
        source="test",
        spec_version="1.0",
        type=CRITERIA_CALC_REQ_EVENT_TYPE,
        text_data=json.dumps(payload)
    )

    await client.middleware.handle(criteria_event)

    response = await client._queue.get()
    assert response.type == "EntityCriteriaCalculationResponse"

    response_data = json.loads(response.text_data)
    assert response_data["success"] is True
    assert response_data["entityId"] == "e1"
    assert response_data["requestId"] == "r1"


@pytest.mark.asyncio
async def test_greet_event_triggers_rollback(mock_dependencies):
    """Test that greet event triggers rollback."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = AsyncMock()

    client = GrpcClient(dispatcher, auth, chat_service)

    greet_event = CloudEvent(
        id="greet_id",
        source="test",
        spec_version="1.0",
        type=GREET_EVENT_TYPE,
        text_data=json.dumps({"message": "hello"})
    )

    await client.middleware.handle(greet_event)

    # Verify rollback was triggered
    mock_dependencies.run_coroutine.assert_called_once()

    # Greet events don't produce responses
    assert client._queue.empty()


@pytest.mark.asyncio
async def test_error_event_processing(mock_dependencies):
    """Test error event processing."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    error_event = CloudEvent(
        id="error_id",
        source="test",
        spec_version="1.0",
        type=ERROR_EVENT_TYPE,
        text_data=json.dumps({
            "code": "TEST_ERROR",
            "message": "Test error message",
            "sourceEventId": "source_123"
        })
    )

    await client.middleware.handle(error_event)

    # Error events don't produce responses
    assert client._queue.empty()


@pytest.mark.asyncio
async def test_ack_event_processing(mock_dependencies):
    """Test ACK event processing."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    ack_event = CloudEvent(
        id="ack_id",
        source="test",
        spec_version="1.0",
        type=EVENT_ACK_TYPE,
        text_data=json.dumps({"sourceEventId": "source_123"})
    )

    await client.middleware.handle(ack_event)

    # ACK events don't produce responses
    assert client._queue.empty()


# ============= Delegation Tests =============

@pytest.mark.asyncio
async def test_start_delegation():
    """Test start method delegation."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    with patch.object(client.facade, 'start') as mock_start:
        mock_start.return_value = asyncio.Future()
        mock_start.return_value.set_result(None)

        await client.start()
        mock_start.assert_called_once()


def test_stop_delegation():
    """Test stop method delegation."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    with patch.object(client.facade, 'stop') as mock_stop:
        client.stop()
        mock_stop.assert_called_once()


def test_on_event_delegation():
    """Test _on_event method delegation."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    event = CloudEvent(id="test", source="test", spec_version="1.0", type="test")

    with patch.object(client.facade, '_on_event') as mock_on_event:
        client._on_event(event)
        mock_on_event.assert_called_once_with(event)


@pytest.mark.asyncio
async def test_consume_stream_delegation():
    """Test consume_stream method delegation."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    with patch.object(client.facade, '_consume_stream') as mock_consume:
        mock_consume.return_value = asyncio.Future()
        mock_consume.return_value.set_result(None)

        await client.consume_stream()
        mock_consume.assert_called_once()


@pytest.mark.asyncio
async def test_grpc_stream_delegation():
    """Test grpc_stream method delegation."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    with patch.object(client.facade, 'start') as mock_start:
        mock_start.return_value = asyncio.Future()
        mock_start.return_value.set_result(None)

        await client.grpc_stream()
        mock_start.assert_called_once()


@pytest.mark.asyncio
async def test_grpc_stream_exception_handling():
    """Test grpc_stream exception handling."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    with patch.object(client.facade, 'start') as mock_start:
        mock_start.side_effect = Exception("Test exception")

        # Should not raise exception
        await client.grpc_stream()
        mock_start.assert_called_once()


# ============= Backward Compatibility Tests =============

def test_public_api_unchanged():
    """Test that public API remains unchanged."""
    dispatcher = MockWorkflowDispatcher()
    auth = MockAuth()
    chat_service = MockChatService()

    client = GrpcClient(dispatcher, auth, chat_service)

    # Verify key methods exist
    essential_methods = [
        'grpc_stream', 'metadata_callback', 'get_grpc_credentials',
        'start', 'stop', '_on_event', 'consume_stream'
    ]

    for method in essential_methods:
        assert hasattr(client, method), f"Method {method} missing"
        assert callable(getattr(client, method)), f"Method {method} not callable"


def test_constants_backward_compatibility():
    """Test that constants are still accessible from grpc_client module."""
    from common.grpc_client.grpc_client import (
        CALC_REQ_EVENT_TYPE, CALC_RESP_EVENT_TYPE,
        JOIN_EVENT_TYPE, EVENT_ACK_TYPE
    )

    assert CALC_REQ_EVENT_TYPE == "EntityProcessorCalculationRequest"
    assert CALC_RESP_EVENT_TYPE == "EntityProcessorCalculationResponse"
    assert JOIN_EVENT_TYPE == "CalculationMemberJoinEvent"
    assert EVENT_ACK_TYPE == "EventAckResponse"


def test_constructor_signature_unchanged():
    """Test that constructor signature is unchanged."""
    import inspect

    sig = inspect.signature(GrpcClient.__init__)
    params = list(sig.parameters.keys())

    expected_params = ['self', 'workflow_dispatcher', 'auth', 'chat_service']
    assert params == expected_params

    # Verify no default values (all required)
    for param_name in expected_params[1:]:
        param = sig.parameters[param_name]
        assert param.default == inspect.Parameter.empty


