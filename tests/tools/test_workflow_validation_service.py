import pytest
import json
import tempfile
import os
from unittest.mock import AsyncMock, patch, mock_open

from tools.workflow_validation_service import WorkflowValidationService
from entity.model import AgenticFlowEntity


class TestWorkflowValidationService:
    """Test cases for WorkflowValidationService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for the service."""
        return {
            'workflow_helper_service': AsyncMock(),
            'entity_service': AsyncMock(),
            'cyoda_auth_service': AsyncMock(),
            'workflow_converter_service': AsyncMock(),
            'scheduler_service': AsyncMock(),
            'data_service': AsyncMock(),
            'dataset': None,
            'mock': True
        }

    @pytest.fixture
    def service(self, mock_dependencies):
        """Create WorkflowValidationService instance."""
        return WorkflowValidationService(**mock_dependencies)

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock agentic flow entity."""
        entity = AgenticFlowEntity(memory_id="test_memory_id")
        entity.workflow_cache = {"git_branch": "test_branch"}
        return entity

    @pytest.fixture
    def sample_workflow_data(self):
        """Sample workflow data for testing."""
        return {
            "states": {
                "state1": {
                    "transitions": {
                        "transition1": {
                            "action": {
                                "config": {
                                    "type": "function",
                                    "function": {
                                        "name": "clone_repo"
                                    }
                                }
                            }
                        },
                        "transition2": {
                            "condition": {
                                "name": "build_new_app_criteria"
                            }
                        }
                    }
                },
                "state2": {
                    "transitions": {
                        "transition3": {
                            "action": {
                                "config": {
                                    "type": "function",
                                    "function": {
                                        "name": "init_chats"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    @pytest.mark.asyncio
    async def test_extract_workflow_components(self, service, sample_workflow_data):
        """Test extraction of processors and criteria from workflow."""
        # Create temporary workflow file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_workflow_data, f)
            temp_file = f.name

        try:
            processors, criteria = await service._extract_workflow_components(temp_file)
            
            assert processors == {"clone_repo", "init_chats"}
            assert criteria == {"build_new_app_criteria"}
        finally:
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_extract_workflow_components_from_directory(self, service, sample_workflow_data):
        """Test extraction of processors and criteria from workflow directory with multiple files."""
        # Create temporary directory with multiple workflow files
        with tempfile.TemporaryDirectory() as temp_dir:
            # First workflow file
            workflow_file1 = os.path.join(temp_dir, "workflow1.json")
            with open(workflow_file1, 'w') as f:
                json.dump(sample_workflow_data, f)

            # Second workflow file with different components
            workflow_data2 = {
                "states": {
                    "state1": {
                        "transitions": {
                            "transition1": {
                                "action": {
                                    "config": {
                                        "type": "function",
                                        "function": {"name": "deploy_app"}
                                    }
                                },
                                "condition": {
                                    "config": {
                                        "type": "function",
                                        "function": {"name": "deployment_ready"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
            workflow_file2 = os.path.join(temp_dir, "workflow2.json")
            with open(workflow_file2, 'w') as f:
                json.dump(workflow_data2, f)

            # Test directory path (should find and process both JSON files)
            processors, criteria = await service._extract_workflow_components(temp_dir)

            # Should include components from both files
            assert processors == {"clone_repo", "init_chats", "deploy_app"}
            assert criteria == {"build_new_app_criteria", "deployment_ready"}

    @pytest.mark.asyncio
    async def test_extract_workflow_components_directory_no_json(self, service):
        """Test extraction from directory with no JSON files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a non-JSON file
            with open(os.path.join(temp_dir, "readme.txt"), 'w') as f:
                f.write("No JSON here")

            # Should raise FileNotFoundError
            with pytest.raises(FileNotFoundError, match="No JSON workflow files found"):
                await service._extract_workflow_components(temp_dir)

    @pytest.mark.asyncio
    async def test_extract_components_from_file(self, service, sample_workflow_data):
        """Test extraction of components from a single workflow file."""
        # Create temporary workflow file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_workflow_data, f)
            temp_file = f.name

        try:
            processors, criteria = await service._extract_components_from_file(temp_file)

            assert processors == {"clone_repo", "init_chats"}
            assert criteria == {"build_new_app_criteria"}
        finally:
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_get_implemented_processors(self, service):
        """Test getting implemented processors from directory."""
        with patch('tools.workflow_validation_service.get_project_file_name') as mock_get_path:
            with patch('os.path.exists', return_value=True):
                with patch('os.path.isdir', return_value=True):
                    with patch('os.listdir', return_value=['CloneRepo.java', 'InitChats.java', 'README.md']):
                        mock_get_path.return_value = "/fake/processor/dir"

                        processors = await service._get_implemented_processors(
                            "test_branch", "test_repo", "src/main/java/com/java_template/application/processor"
                        )

                        assert processors == {"CloneRepo", "InitChats"}

    @pytest.mark.asyncio
    async def test_get_implemented_criteria(self, service):
        """Test getting implemented criteria from directory."""
        with patch('tools.workflow_validation_service.get_project_file_name') as mock_get_path:
            with patch('os.path.exists', return_value=True):
                with patch('os.path.isdir', return_value=True):
                    with patch('os.listdir', return_value=['BuildNewAppCriteria.java', 'TestCriteria.java']):
                        mock_get_path.return_value = "/fake/criteria/dir"

                        criteria = await service._get_implemented_criteria(
                            "test_branch", "test_repo", "src/main/java/com/java_template/application/criteria"
                        )

                        assert criteria == {"BuildNewAppCriteria", "TestCriteria"}

    def test_validate_implementation_success(self, service):
        """Test successful validation when all components match."""
        expected_processors = {"clone_repo", "init_chats"}
        expected_criteria = {"build_new_app_criteria"}
        implemented_processors = {"clone_repo", "init_chats"}
        implemented_criteria = {"build_new_app_criteria"}
        
        result = service._validate_implementation(
            expected_processors, expected_criteria,
            implemented_processors, implemented_criteria
        )
        
        assert "✅ Workflow implementation validation passed!" in result

    def test_validate_implementation_missing_components(self, service):
        """Test validation with missing components."""
        expected_processors = {"clone_repo", "init_chats", "missing_processor"}
        expected_criteria = {"build_new_app_criteria", "missing_criteria"}
        implemented_processors = {"clone_repo", "init_chats"}
        implemented_criteria = {"build_new_app_criteria"}
        
        result = service._validate_implementation(
            expected_processors, expected_criteria,
            implemented_processors, implemented_criteria
        )
        
        assert "❌ Workflow implementation validation failed:" in result
        assert "Missing processors: missing_processor" in result
        assert "Missing criteria: missing_criteria" in result

    def test_validate_implementation_extra_components(self, service):
        """Test validation with extra components (should pass but report extras)."""
        expected_processors = {"clone_repo"}
        expected_criteria = {"build_new_app_criteria"}
        implemented_processors = {"clone_repo", "extra_processor"}
        implemented_criteria = {"build_new_app_criteria", "extra_criteria"}

        result = service._validate_implementation(
            expected_processors, expected_criteria,
            implemented_processors, implemented_criteria
        )

        assert "✅ Workflow implementation validation passed!" in result
        assert "Extra processors found (keeping them): extra_processor" in result
        assert "Extra criteria found (keeping them): extra_criteria" in result

    def test_validate_implementation_mixed_issues(self, service):
        """Test validation with mixed issues."""
        expected_processors = {"clone_repo", "init_chats", "missing_processor"}
        expected_criteria = {"build_new_app_criteria", "missing_criteria"}
        implemented_processors = {"clone_repo", "wrong_processor"}  # missing init_chats, has extra
        implemented_criteria = {"wrong_criteria"}  # missing build_new_app_criteria, has extra

        result = service._validate_implementation(
            expected_processors, expected_criteria,
            implemented_processors, implemented_criteria
        )

        assert "❌ Workflow implementation validation failed:" in result
        assert "Missing processors: init_chats, missing_processor" in result
        assert "Extra processors found (keeping them): wrong_processor" in result
        assert "Missing criteria: build_new_app_criteria, missing_criteria" in result
        assert "Extra criteria found (keeping them): wrong_criteria" in result

    @pytest.mark.asyncio
    async def test_validate_workflow_implementation_integration(self, service, mock_agentic_entity, sample_workflow_data):
        """Test the main validation method integration."""
        with patch('tools.workflow_validation_service.resolve_repository_name_with_language_param', return_value="test_repo"):
            with patch('tools.workflow_validation_service.get_project_file_name') as mock_get_path:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(sample_workflow_data, f)
                    temp_file = f.name

                try:
                    mock_get_path.side_effect = [
                        temp_file,  # workflow file
                        "/fake/processor/dir",  # processor directory
                        "/fake/criteria/dir"  # criteria directory
                    ]

                    with patch('os.path.exists', return_value=True):
                        with patch('os.path.isdir') as mock_isdir:
                            # Only directories should return True for isdir
                            def isdir_side_effect(path):
                                return path in ["/fake/processor/dir", "/fake/criteria/dir"]
                            mock_isdir.side_effect = isdir_side_effect

                            with patch('os.listdir') as mock_listdir:
                                # Mock processor and criteria directories
                                mock_listdir.side_effect = [
                                    ['clone_repo.java', 'init_chats.java'],  # processors
                                    ['build_new_app_criteria.java']  # criteria
                                ]

                                result = await service.validate_workflow_implementation(
                                    "test_id", mock_agentic_entity,
                                    workflow_file_path="com/java_template/application/workflow",
                                    processors_path="src/main/java/com/java_template/application/processor",
                                    criteria_path="src/main/java/com/java_template/application/criteria"
                                )

                                assert "✅ Workflow implementation validation passed!" in result
                finally:
                    os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_validate_workflow_implementation_error_handling(self, service, mock_agentic_entity):
        """Test error handling in validation method."""
        with patch('tools.workflow_validation_service.resolve_repository_name_with_language_param', side_effect=Exception("Test error")):
            result = await service.validate_workflow_implementation(
                "test_id", mock_agentic_entity
            )

            assert "Error validating workflow implementation" in result

    def test_service_inheritance(self, service):
        """Test that service properly inherits from BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        assert isinstance(service, BaseWorkflowService)
        assert hasattr(service, 'logger')
        assert hasattr(service, '_handle_error')
        assert hasattr(service, '_validate_required_params')
