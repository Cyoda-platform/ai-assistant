"""
Simple test to verify the test infrastructure works.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_basic_import():
    """Test that we can import the base service."""
    from tools.base_service import BaseWorkflowService
    assert BaseWorkflowService is not None


def test_mock_functionality():
    """Test that mocking works correctly."""
    mock_obj = MagicMock()
    mock_obj.test_method.return_value = "test_result"
    
    result = mock_obj.test_method()
    assert result == "test_result"
    mock_obj.test_method.assert_called_once()


@pytest.mark.asyncio
async def test_async_mock():
    """Test that async mocking works correctly."""
    mock_async = AsyncMock()
    mock_async.async_method.return_value = "async_result"
    
    result = await mock_async.async_method()
    assert result == "async_result"
    mock_async.async_method.assert_called_once()


def test_base_service_creation():
    """Test that we can create a BaseWorkflowService instance."""
    from tools.base_service import BaseWorkflowService
    
    # Create mock dependencies
    mock_deps = {
        'workflow_helper_service': AsyncMock(),
        'entity_service': AsyncMock(),
        'cyoda_auth_service': MagicMock(),
        'workflow_converter_service': AsyncMock(),
        'scheduler_service': AsyncMock(),
        'data_service': AsyncMock(),
    }
    
    # Create service instance
    service = BaseWorkflowService(**mock_deps)
    
    # Verify it was created successfully
    assert service is not None
    assert service.workflow_helper_service is not None
    assert service.entity_service is not None
    assert service.logger is not None


def test_parse_from_string():
    """Test the parse_from_string utility method."""
    from tools.base_service import BaseWorkflowService
    
    mock_deps = {
        'workflow_helper_service': AsyncMock(),
        'entity_service': AsyncMock(),
        'cyoda_auth_service': MagicMock(),
        'workflow_converter_service': AsyncMock(),
        'scheduler_service': AsyncMock(),
        'data_service': AsyncMock(),
    }
    
    service = BaseWorkflowService(**mock_deps)
    
    # Test string parsing
    escaped_string = "Hello\\nWorld\\t!"
    result = service.parse_from_string(escaped_string)
    
    assert result == "Hello\nWorld\t!"


@pytest.mark.asyncio
async def test_validate_required_params():
    """Test parameter validation."""
    from tools.base_service import BaseWorkflowService
    
    mock_deps = {
        'workflow_helper_service': AsyncMock(),
        'entity_service': AsyncMock(),
        'cyoda_auth_service': MagicMock(),
        'workflow_converter_service': AsyncMock(),
        'scheduler_service': AsyncMock(),
        'data_service': AsyncMock(),
    }
    
    service = BaseWorkflowService(**mock_deps)
    
    # Test with all required params present
    params = {"param1": "value1", "param2": "value2"}
    required = ["param1", "param2"]
    
    is_valid, error_msg = await service._validate_required_params(params, required)
    
    assert is_valid is True
    assert error_msg == ""
    
    # Test with missing params
    params = {"param1": "value1"}
    required = ["param1", "param2"]
    
    is_valid, error_msg = await service._validate_required_params(params, required)
    
    assert is_valid is False
    assert "Missing required parameters" in error_msg


def test_file_operations_service_creation():
    """Test that we can create a FileOperationsService instance."""
    from tools.file_operations_service import FileOperationsService
    
    mock_deps = {
        'workflow_helper_service': AsyncMock(),
        'entity_service': AsyncMock(),
        'cyoda_auth_service': MagicMock(),
        'workflow_converter_service': AsyncMock(),
        'scheduler_service': AsyncMock(),
        'data_service': AsyncMock(),
    }
    
    service = FileOperationsService(**mock_deps)
    
    assert service is not None
    assert hasattr(service, 'save_file')
    assert hasattr(service, 'read_file')
    assert hasattr(service, 'clone_repo')


def test_web_operations_service_creation():
    """Test that we can create a WebOperationsService instance."""
    from tools.web_operations_service import WebOperationsService
    
    mock_deps = {
        'workflow_helper_service': AsyncMock(),
        'entity_service': AsyncMock(),
        'cyoda_auth_service': MagicMock(),
        'workflow_converter_service': AsyncMock(),
        'scheduler_service': AsyncMock(),
        'data_service': AsyncMock(),
    }
    
    service = WebOperationsService(**mock_deps)
    
    assert service is not None
    assert hasattr(service, 'web_search')
    assert hasattr(service, 'read_link')
    assert hasattr(service, 'web_scrape')


def test_core_services_can_be_imported():
    """Test that core service classes can be imported successfully."""
    services = [
        'tools.base_service.BaseWorkflowService',
        'tools.file_operations_service.FileOperationsService',
        'tools.web_operations_service.WebOperationsService',
        'tools.state_management_service.StateManagementService',
        'tools.deployment_service.DeploymentService',
        'tools.application_builder_service.ApplicationBuilderService',
        'tools.application_editor_service.ApplicationEditorService',
        'tools.utility_service.UtilityService',
        # Skip workflow_management_service due to libcst dependency
    ]

    for service_path in services:
        module_path, class_name = service_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        service_class = getattr(module, class_name)
        assert service_class is not None


def test_workflow_management_service_import():
    """Test workflow management service import separately (may fail due to dependencies)."""
    try:
        from tools.workflow_management_service import WorkflowManagementService
        assert WorkflowManagementService is not None
    except ImportError as e:
        # This is expected if libcst is not available
        assert "libcst" in str(e) or "No module named" in str(e)


def test_dispatcher_components_can_be_imported():
    """Test that all dispatcher components can be imported successfully."""
    components = [
        'workflow.dispatcher.event_processor.EventProcessor',
        'workflow.dispatcher.ai_agent_handler.AIAgentHandler',
        'workflow.dispatcher.memory_manager.MemoryManager',
        'workflow.dispatcher.workflow_dispatcher.WorkflowDispatcher',
    ]
    
    for component_path in components:
        module_path, class_name = component_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        component_class = getattr(module, class_name)
        assert component_class is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
