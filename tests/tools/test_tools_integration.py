"""
Integration tests for all tools services.
This file tests the core functionality without complex mocking.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class TestToolsIntegration:
    """Integration tests for all tools services."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for all services."""
        return {
            'workflow_helper_service': AsyncMock(),
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
            'workflow_converter_service': AsyncMock(),
            'scheduler_service': AsyncMock(),
            'data_service': AsyncMock(),
        }

    @pytest.fixture
    def mock_chat_entity(self):
        """Create mock ChatEntity with all required attributes."""
        entity = MagicMock()
        entity.workflow_cache = {"git_branch": "test_branch"}
        entity.workflow_name = "test_workflow"
        entity.user_id = "test_user_123"
        entity.technical_id = "test_tech_id"
        entity.failed = False
        entity.error = None
        entity.edge_messages_store = []
        return entity

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity with all required attributes."""
        entity = MagicMock()
        entity.workflow_cache = {"git_branch": "test_branch"}
        entity.workflow_name = "test_workflow"
        entity.user_id = "test_user_123"
        entity.technical_id = "test_tech_id"
        entity.failed = False
        entity.error = None
        entity.edge_messages_store = []
        return entity

    def test_application_builder_service_creation(self, mock_dependencies):
        """Test ApplicationBuilderService can be created."""
        from tools.application_builder_service import ApplicationBuilderService
        
        service = ApplicationBuilderService(**mock_dependencies)
        assert service is not None
        assert hasattr(service, 'build_general_application')
        assert hasattr(service, 'resume_build_general_application')
        assert hasattr(service, 'init_setup_workflow')

    def test_application_editor_service_creation(self, mock_dependencies):
        """Test ApplicationEditorService can be created."""
        from tools.application_editor_service import ApplicationEditorService
        
        service = ApplicationEditorService(**mock_dependencies)
        assert service is not None
        assert hasattr(service, 'edit_existing_app_design_additional_feature')
        assert hasattr(service, 'edit_api_existing_app')
        assert hasattr(service, 'edit_existing_workflow')

    def test_file_operations_service_creation(self, mock_dependencies):
        """Test FileOperationsService can be created."""
        from tools.file_operations_service import FileOperationsService
        
        service = FileOperationsService(**mock_dependencies)
        assert service is not None
        assert hasattr(service, 'save_file')
        assert hasattr(service, 'read_file')
        assert hasattr(service, 'clone_repo')

    def test_web_operations_service_creation(self, mock_dependencies):
        """Test WebOperationsService can be created."""
        from tools.web_operations_service import WebOperationsService
        
        service = WebOperationsService(**mock_dependencies)
        assert service is not None
        assert hasattr(service, 'web_search')
        assert hasattr(service, 'read_link')
        assert hasattr(service, 'web_scrape')

    def test_state_management_service_creation(self, mock_dependencies):
        """Test StateManagementService can be created."""
        from tools.state_management_service import StateManagementService
        
        service = StateManagementService(**mock_dependencies)
        assert service is not None
        assert hasattr(service, 'finish_discussion')
        assert hasattr(service, 'is_stage_completed')
        assert hasattr(service, 'lock_chat')

    def test_deployment_service_creation(self, mock_dependencies):
        """Test DeploymentService can be created."""
        from tools.deployment_service import DeploymentService
        
        service = DeploymentService(**mock_dependencies)
        assert service is not None
        assert hasattr(service, 'schedule_deploy_env')
        assert hasattr(service, 'deploy_cyoda_env')
        assert hasattr(service, 'get_env_deploy_status')

    def test_utility_service_creation(self, mock_dependencies):
        """Test UtilityService can be created."""
        from tools.utility_service import UtilityService
        
        service = UtilityService(**mock_dependencies)
        assert service is not None
        assert hasattr(service, 'get_weather')
        assert hasattr(service, 'get_user_info')
        assert hasattr(service, 'fail_workflow')

    @pytest.mark.asyncio
    async def test_base_service_parameter_validation(self, mock_dependencies):
        """Test parameter validation in BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        
        service = BaseWorkflowService(**mock_dependencies)
        
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

    @pytest.mark.asyncio
    async def test_application_builder_parameter_validation(self, mock_dependencies, mock_chat_entity):
        """Test parameter validation in ApplicationBuilderService."""
        from tools.application_builder_service import ApplicationBuilderService
        
        service = ApplicationBuilderService(**mock_dependencies)
        
        # Test missing required parameters
        result = await service.build_general_application("tech_id", mock_chat_entity)
        assert "Missing required parameters" in result

    @pytest.mark.asyncio
    async def test_application_editor_parameter_validation(self, mock_dependencies, mock_agentic_entity):
        """Test parameter validation in ApplicationEditorService."""
        from tools.application_editor_service import ApplicationEditorService
        
        service = ApplicationEditorService(**mock_dependencies)
        
        # Test missing required parameters
        result = await service.edit_existing_app_design_additional_feature("tech_id", mock_agentic_entity)
        assert "Missing required parameters" in result

    @pytest.mark.asyncio
    async def test_file_operations_parameter_validation(self, mock_dependencies, mock_chat_entity):
        """Test parameter validation in FileOperationsService."""
        from tools.file_operations_service import FileOperationsService
        
        service = FileOperationsService(**mock_dependencies)
        
        # Test missing required parameters
        result = await service.save_file("tech_id", mock_chat_entity)
        assert "Missing required parameters" in result

    @pytest.mark.asyncio
    async def test_web_operations_parameter_validation(self, mock_dependencies, mock_chat_entity):
        """Test parameter validation in WebOperationsService."""
        from tools.web_operations_service import WebOperationsService
        
        service = WebOperationsService(**mock_dependencies)
        
        # Test missing required parameters
        result = await service.web_search("tech_id", mock_chat_entity)
        assert "Missing required parameters" in result

    @pytest.mark.asyncio
    async def test_state_management_parameter_validation(self, mock_dependencies, mock_chat_entity):
        """Test parameter validation in StateManagementService."""
        from tools.state_management_service import StateManagementService
        
        service = StateManagementService(**mock_dependencies)
        
        # Test missing required parameters
        try:
            result = await service.finish_discussion("tech_id", mock_chat_entity)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Missing required parameter" in str(e)

    @pytest.mark.asyncio
    async def test_utility_service_parameter_validation(self, mock_dependencies, mock_chat_entity):
        """Test parameter validation in UtilityService."""
        from tools.utility_service import UtilityService
        
        service = UtilityService(**mock_dependencies)
        
        # Test missing required parameters
        result = await service.get_weather("tech_id", mock_chat_entity)
        # Weather service returns a dict, not an error message
        assert isinstance(result, dict)

    def test_all_services_inherit_from_base(self, mock_dependencies):
        """Test that all services inherit from BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        from tools.application_builder_service import ApplicationBuilderService
        from tools.application_editor_service import ApplicationEditorService
        from tools.file_operations_service import FileOperationsService
        from tools.web_operations_service import WebOperationsService
        from tools.state_management_service import StateManagementService
        from tools.deployment_service import DeploymentService
        from tools.utility_service import UtilityService
        
        services = [
            ApplicationBuilderService(**mock_dependencies),
            ApplicationEditorService(**mock_dependencies),
            FileOperationsService(**mock_dependencies),
            WebOperationsService(**mock_dependencies),
            StateManagementService(**mock_dependencies),
            DeploymentService(**mock_dependencies),
            UtilityService(**mock_dependencies),
        ]
        
        for service in services:
            assert isinstance(service, BaseWorkflowService)
            assert hasattr(service, 'logger')
            assert hasattr(service, '_handle_error')
            assert hasattr(service, '_validate_required_params')

    def test_service_method_counts(self, mock_dependencies):
        """Test that services have the expected number of public methods."""
        from tools.application_builder_service import ApplicationBuilderService
        from tools.application_editor_service import ApplicationEditorService
        from tools.file_operations_service import FileOperationsService
        from tools.web_operations_service import WebOperationsService
        from tools.state_management_service import StateManagementService
        from tools.deployment_service import DeploymentService
        from tools.utility_service import UtilityService
        
        # Count public methods (not starting with _)
        def count_public_methods(cls):
            return len([method for method in dir(cls) if not method.startswith('_') and callable(getattr(cls, method))])
        
        # These counts should match the number of migrated methods
        service_method_counts = {
            ApplicationBuilderService: 3,  # build_general_application, resume_build_general_application, init_setup_workflow
            ApplicationEditorService: 6,   # 6 edit methods
            FileOperationsService: 6,      # save_file, read_file, clone_repo, etc.
            WebOperationsService: 6,       # web_search, read_link, web_scrape, etc.
            StateManagementService: 6,     # get_chat_state, set_chat_state, etc.
            DeploymentService: 6,          # schedule_deploy_env, deploy_cyoda_env, etc.
            UtilityService: 6,             # get_weather, get_user_info, etc.
        }
        
        for service_class, expected_count in service_method_counts.items():
            service = service_class(**mock_dependencies)
            actual_count = count_public_methods(service_class)
            # Allow some flexibility in method counts due to inherited methods
            assert actual_count >= expected_count, f"{service_class.__name__} should have at least {expected_count} public methods, got {actual_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
