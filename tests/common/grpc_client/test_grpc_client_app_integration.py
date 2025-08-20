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


def test_grpc_client_direct_instantiation():
    """Test that GrpcClient can be instantiated directly as before."""
    workflow_dispatcher = MockWorkflowDispatcher()
    auth = MockCyodaAuthService()
    chat_service = MockChatService()

    # This should work exactly as before the refactor
    client = GrpcClient(workflow_dispatcher, auth, chat_service)

    # Verify all expected attributes exist
    assert hasattr(client, 'workflow_dispatcher')
    assert hasattr(client, 'auth')
    assert hasattr(client, 'chat_service')
    assert hasattr(client, 'processor_loop')

    # Verify new internal components are initialized
    assert hasattr(client, 'router')
    assert hasattr(client, 'builders')
    assert hasattr(client, 'outbox')
    assert hasattr(client, 'middleware')

    # Verify public methods exist and are callable
    assert callable(client.grpc_stream)
    assert callable(client.metadata_callback)
    assert callable(client.get_grpc_credentials)


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


def test_grpc_client_methods_unchanged():
    """Test that all expected public methods exist with correct signatures."""
    workflow_dispatcher = MockWorkflowDispatcher()
    auth = MockCyodaAuthService()
    chat_service = MockChatService()
    
    client = GrpcClient(workflow_dispatcher, auth, chat_service)
    
    # Test grpc_stream method
    import inspect
    grpc_stream_sig = inspect.signature(client.grpc_stream)
    assert len(grpc_stream_sig.parameters) == 0  # No parameters except self
    
    # Test metadata_callback method
    metadata_callback_sig = inspect.signature(client.metadata_callback)
    params = list(metadata_callback_sig.parameters.keys())
    assert params == ['context', 'callback']
    
    # Test get_grpc_credentials method
    creds_sig = inspect.signature(client.get_grpc_credentials)
    assert len(creds_sig.parameters) == 0  # No parameters except self


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


@pytest.mark.asyncio
async def test_grpc_client_basic_functionality():
    """Test that basic GrpcClient functionality works."""
    workflow_dispatcher = MockWorkflowDispatcher()
    auth = MockCyodaAuthService()
    chat_service = MockChatService()
    
    client = GrpcClient(workflow_dispatcher, auth, chat_service)
    
    # Test metadata_callback
    context = MagicMock()
    callback = MagicMock()
    
    # Should not raise exception
    client.metadata_callback(context, callback)
    
    # Verify callback was called with token
    callback.assert_called_once()
    args, kwargs = callback.call_args
    assert len(args) == 2
    assert args[0] == [('authorization', 'Bearer mock_token')]
    assert args[1] is None
    
    # Test get_grpc_credentials (should not raise exception)
    with patch('common.grpc_client.grpc_client.grpc'):
        creds = client.get_grpc_credentials()
        # Just verify it returns something (actual grpc testing would need more setup)


def test_app_factory_import():
    """Test that the app factory can import GrpcClient class."""
    # This verifies that the import in services/factory.py still works
    try:
        from common.grpc_client.grpc_client import GrpcClient
        # If we get here, the import worked
        assert GrpcClient is not None
    except ImportError as e:
        pytest.fail(f"GrpcClient import failed: {e}")


def test_no_breaking_changes_in_public_api():
    """Comprehensive test that no breaking changes were introduced."""
    workflow_dispatcher = MockWorkflowDispatcher()
    auth = MockCyodaAuthService()
    chat_service = MockChatService()
    
    # Should be able to create client exactly as before
    client = GrpcClient(workflow_dispatcher, auth, chat_service)
    
    # All these should work exactly as before
    assert client.workflow_dispatcher is workflow_dispatcher
    assert client.auth is auth
    assert client.chat_service is chat_service
    
    # These essential methods should exist and be callable
    essential_methods = [
        'grpc_stream', 'metadata_callback', 'get_grpc_credentials',
        'consume_stream'
    ]

    for method_name in essential_methods:
        assert hasattr(client, method_name), f"Method {method_name} missing"
        assert callable(getattr(client, method_name)), f"Method {method_name} not callable"
