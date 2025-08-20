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


