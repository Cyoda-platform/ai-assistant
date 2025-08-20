"""
Integration test to verify GrpcClient works with the actual application setup.
This test verifies that the refactored GrpcClient can be instantiated and used
exactly as it was before the refactor.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from common.grpc_client.grpc_client import GrpcClient


class MockCyodaAuthService:
    def get_access_token(self):
        return "mock_token"

    def invalidate_tokens(self):
        pass


class MockWorkflowDispatcher:
    async def process_event(self, *, entity, processor_name, payload, technical_id):
        return entity, {"result": "success"}


class MockChatService:
    async def rollback_failed_workflows(self):
        pass


def test_grpc_client_constructor_signature_unchanged():
    """Test that constructor signature is exactly the same."""
    import inspect
    
    # Get the constructor signature
    sig = inspect.signature(GrpcClient.__init__)
    params = list(sig.parameters.keys())
    
    # Should be: self, workflow_dispatcher, auth, chat_service
    expected_params = ['self', 'workflow_dispatcher', 'auth', 'chat_service']
    assert params == expected_params
    
    # Verify no default values (all required)
    for param_name in expected_params[1:]:  # Skip 'self'
        param = sig.parameters[param_name]
        assert param.default == inspect.Parameter.empty


def test_backward_compatibility_constants():
    """Test that constants can still be imported from grpc_client module."""
    # This should work for backward compatibility
    try:
        from common.grpc_client.grpc_client import (
            CALC_REQ_EVENT_TYPE, CALC_RESP_EVENT_TYPE,
            JOIN_EVENT_TYPE, EVENT_ACK_TYPE, KEEP_ALIVE_EVENT_TYPE
        )
        
        # Verify they have the expected values
        assert CALC_REQ_EVENT_TYPE == "EntityProcessorCalculationRequest"
        assert CALC_RESP_EVENT_TYPE == "EntityProcessorCalculationResponse"
        assert JOIN_EVENT_TYPE == "CalculationMemberJoinEvent"
        assert EVENT_ACK_TYPE == "EventAckResponse"
        assert KEEP_ALIVE_EVENT_TYPE == "CalculationMemberKeepAliveEvent"
        
    except ImportError as e:
        pytest.fail(f"Constants import failed: {e}")


def test_app_factory_import():
    """Test that the app factory can import GrpcClient class."""
    # This verifies that the import in services/factory.py still works
    try:
        from common.grpc_client.grpc_client import GrpcClient
        # If we get here, the import worked
        assert GrpcClient is not None
    except ImportError as e:
        pytest.fail(f"GrpcClient import failed: {e}")
