import pytest
import json
import os
import tempfile
import shutil
from unittest.mock import AsyncMock, MagicMock, patch

from tools.workflow_processor_validation_service import WorkflowProcessorValidationService
from entity.model import AgenticFlowEntity


class TestWorkflowProcessorValidationService:
    
    @pytest.fixture
    def setup_method(self):
        """Setup for each test method."""
        # Mock dependencies
        self.workflow_helper_service = AsyncMock()
        self.entity_service = AsyncMock()
        self.cyoda_auth_service = AsyncMock()
        self.workflow_converter_service = AsyncMock()
        self.scheduler_service = AsyncMock()
        self.data_service = AsyncMock()
        self.dataset = MagicMock()
        
        # Create service instance
        self.service = WorkflowProcessorValidationService(
            workflow_helper_service=self.workflow_helper_service,
            entity_service=self.entity_service,
            cyoda_auth_service=self.cyoda_auth_service,
            workflow_converter_service=self.workflow_converter_service,
            scheduler_service=self.scheduler_service,
            data_service=self.data_service,
            dataset=self.dataset,
            mock=True
        )
        
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.workflow_dir = os.path.join(self.temp_dir, "workflow")
        self.processor_dir = os.path.join(self.temp_dir, "processor")
        self.criteria_dir = os.path.join(self.temp_dir, "criteria")
        
        os.makedirs(self.workflow_dir)
        os.makedirs(self.processor_dir)
        os.makedirs(self.criteria_dir)
        
        yield
        
        # Cleanup
        shutil.rmtree(self.temp_dir)

    def create_workflow_file(self, filename: str, workflow_data: dict):
        """Helper to create workflow JSON files"""
        file_path = os.path.join(self.workflow_dir, filename)
        with open(file_path, 'w') as f:
            json.dump(workflow_data, f)

    def create_java_file(self, directory: str, filename: str, content: str = "// Java class"):
        """Helper to create Java files"""
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w') as f:
            f.write(content)

    @pytest.mark.asyncio
    async def test_validate_workflow_processors_success(self, setup_method):
        """Test successful validation with matching processors and criteria"""
        
        # Create test workflow with processors and criteria
        workflow_data = {
            "states": {
                "state1": {
                    "transitions": [
                        {
                            "processors": [
                                {"name": "AgentProcessor.user_registration_processor"}
                            ],
                            "criterion": {
                                "type": "function",
                                "function": {"name": "validateUserData"}
                            }
                        }
                    ]
                }
            }
        }
        
        self.create_workflow_file("test_workflow.json", workflow_data)
        
        # Create matching Java files
        self.create_java_file(self.processor_dir, "UserRegistrationProcessor.java")
        self.create_java_file(self.criteria_dir, "validateUserData.java")
        
        # Mock entity and parameters
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {"git_branch_id": "main"}
        
        params = {
            "workflow_directory": "workflow",
            "processor_directory": "processor", 
            "criteria_directory": "criteria"
        }
        
        # Mock get_project_file_name to return our temp directories
        with patch('tools.workflow_processor_validation_service.get_project_file_name') as mock_get_file:
            mock_get_file.side_effect = [self.workflow_dir, self.processor_dir, self.criteria_dir]
            
            # Mock repository resolver
            with patch('tools.workflow_processor_validation_service.resolve_repository_name_with_language_param') as mock_resolver:
                mock_resolver.return_value = "test-repo"
                
                # Execute validation
                result = await self.service.validate_workflow_processors("tech123", entity, **params)
                
                # Verify results
                assert "VALIDATION PASSED" in result
                assert "UserRegistrationProcessor" in result
                assert "validateUserData" in result
                assert "Missing processors: 0" in result
                assert "Missing criteria: 0" in result

    @pytest.mark.asyncio
    async def test_validate_workflow_processors_missing_components(self, setup_method):
        """Test validation with missing processors and criteria"""
        
        # Create test workflow with processors and criteria
        workflow_data = {
            "states": {
                "state1": {
                    "transitions": [
                        {
                            "processors": [
                                {"name": "AgentProcessor.user_registration_processor"},
                                {"name": "AgentProcessor.email_notification_processor"}
                            ],
                            "criterion": {
                                "type": "function",
                                "function": {"name": "validateUserData"}
                            }
                        }
                    ]
                }
            }
        }
        
        self.create_workflow_file("test_workflow.json", workflow_data)
        
        # Create only one of the required Java files (missing EmailNotificationProcessor and validateUserData)
        self.create_java_file(self.processor_dir, "UserRegistrationProcessor.java")
        
        # Mock entity and parameters
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {"git_branch_id": "main"}
        
        params = {
            "workflow_directory": "workflow",
            "processor_directory": "processor",
            "criteria_directory": "criteria"
        }
        
        # Mock get_project_file_name to return our temp directories
        with patch('tools.workflow_processor_validation_service.get_project_file_name') as mock_get_file:
            mock_get_file.side_effect = [self.workflow_dir, self.processor_dir, self.criteria_dir]
            
            # Mock repository resolver
            with patch('tools.workflow_processor_validation_service.resolve_repository_name_with_language_param') as mock_resolver:
                mock_resolver.return_value = "test-repo"
                
                # Execute validation
                result = await self.service.validate_workflow_processors("tech123", entity, **params)
                
                # Verify results
                assert "VALIDATION FAILED" in result
                assert "EmailNotificationProcessor" in result
                assert "validateUserData" in result
                assert "Missing processors: 1" in result
                assert "Missing criteria: 1" in result
                assert "UserRegistrationProcessor" in result  # Should show as found

    @pytest.mark.asyncio
    async def test_validate_workflow_processors_invalid_params(self, setup_method):
        """Test validation with missing required parameters"""
        
        entity = MagicMock(spec=AgenticFlowEntity)
        
        # Missing required parameters
        params = {
            "workflow_directory": "workflow"
            # Missing processor_directory and criteria_directory
        }
        
        result = await self.service.validate_workflow_processors("tech123", entity, **params)
        
        # Should return error message about missing parameters
        assert "Missing required parameter" in result or "required" in result.lower()

    @pytest.mark.asyncio
    async def test_extract_workflow_components(self, setup_method):
        """Test extraction of processors and criteria from workflow data"""
        
        # Create complex workflow data
        workflow_data = {
            "states": {
                "state1": {
                    "transitions": [
                        {
                            "processors": [
                                {"name": "AgentProcessor.user_registration_processor"},
                                {"name": "AgentProcessor.email_notification_processor"}
                            ],
                            "criterion": {
                                "type": "function",
                                "function": {"name": "validateUserData"}
                            }
                        }
                    ]
                },
                "state2": {
                    "transitions": [
                        {
                            "processors": [
                                {"name": "AgentProcessor.payment_processor"}
                            ],
                            "criterion": {
                                "type": "function", 
                                "function": {"name": "validatePayment"}
                            }
                        }
                    ]
                }
            }
        }
        
        self.create_workflow_file("complex_workflow.json", workflow_data)
        
        # Test extraction
        processors, criteria = await self.service._extract_workflow_components(self.workflow_dir)
        
        # Verify extracted components
        expected_processors = {"UserRegistrationProcessor", "EmailNotificationProcessor", "PaymentProcessor"}
        expected_criteria = {"validateUserData", "validatePayment"}
        
        assert processors == expected_processors
        assert criteria == expected_criteria

    def test_to_pascal_case(self, setup_method):
        """Test snake_case to PascalCase conversion"""
        
        test_cases = [
            ("user_registration_processor", "UserRegistrationProcessor"),
            ("email_notification_processor", "EmailNotificationProcessor"),
            ("simple_processor", "SimpleProcessor"),
            ("single", "Single"),
            ("multi_word_long_processor", "MultiWordLongProcessor")
        ]
        
        for snake_case, expected_pascal in test_cases:
            result = self.service._to_pascal_case(snake_case)
            assert result == expected_pascal, f"Expected {expected_pascal}, got {result} for {snake_case}"

    @pytest.mark.asyncio
    async def test_get_existing_files(self, setup_method):
        """Test scanning directory for existing files"""
        
        # Create test Java files
        test_files = [
            "UserRegistrationProcessor.java",
            "EmailNotificationProcessor.java", 
            "PaymentProcessor.java"
        ]
        
        for filename in test_files:
            self.create_java_file(self.processor_dir, filename)
        
        # Also create a non-Java file that should be ignored
        self.create_java_file(self.processor_dir, "README.txt", "Not a Java file")
        
        # Test file scanning
        existing_files = await self.service._get_existing_files(self.processor_dir, '.java')
        
        expected_files = {"UserRegistrationProcessor", "EmailNotificationProcessor", "PaymentProcessor"}
        assert existing_files == expected_files

    @pytest.mark.asyncio
    async def test_validate_workflow_processors_empty_directories(self, setup_method):
        """Test validation with empty directories"""
        
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {"git_branch_id": "main"}
        
        params = {
            "workflow_directory": "workflow",
            "processor_directory": "processor",
            "criteria_directory": "criteria"
        }
        
        # Mock get_project_file_name to return our empty temp directories
        with patch('tools.workflow_processor_validation_service.get_project_file_name') as mock_get_file:
            mock_get_file.side_effect = [self.workflow_dir, self.processor_dir, self.criteria_dir]
            
            # Mock repository resolver
            with patch('tools.workflow_processor_validation_service.resolve_repository_name_with_language_param') as mock_resolver:
                mock_resolver.return_value = "test-repo"
                
                # Execute validation
                result = await self.service.validate_workflow_processors("tech123", entity, **params)
                
                # Should handle empty directories gracefully
                assert "VALIDATION PASSED" in result  # No requirements, so validation passes
                assert "Workflow processors required: 0" in result
                assert "Workflow criteria required: 0" in result
