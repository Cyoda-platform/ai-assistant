import pytest
import json
import os
import tempfile
import shutil
from unittest.mock import AsyncMock, MagicMock, patch

from tools.workflow_component_extraction_service import WorkflowComponentExtractionService
from entity.model import AgenticFlowEntity


class TestWorkflowComponentExtractionService:
    
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
        self.service = WorkflowComponentExtractionService(
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
        os.makedirs(self.workflow_dir)
        
        yield
        
        # Cleanup
        shutil.rmtree(self.temp_dir)

    def create_workflow_file(self, filename: str, workflow_data: dict):
        """Helper to create workflow JSON files"""
        file_path = os.path.join(self.workflow_dir, filename)
        with open(file_path, 'w') as f:
            json.dump(workflow_data, f)

    @pytest.mark.asyncio
    async def test_extract_workflow_components_detailed(self, setup_method):
        """Test extraction with detailed output format"""
        
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
        
        self.create_workflow_file("test_workflow.json", workflow_data)
        
        # Mock entity and parameters
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {"git_branch_id": "main"}
        
        params = {
            "workflow_directory": "workflow",
            "output_format": "detailed"
        }
        
        # Mock get_project_file_name to return our temp directory
        with patch('tools.workflow_component_extraction_service.get_project_file_name') as mock_get_file:
            mock_get_file.return_value = self.workflow_dir
            
            # Mock repository resolver
            with patch('tools.workflow_component_extraction_service.resolve_repository_name_with_language_param') as mock_resolver:
                mock_resolver.return_value = "test-repo"
                
                # Execute extraction
                result = await self.service.extract_workflow_components("tech123", entity, **params)
                
                # Verify results
                assert "WORKFLOW COMPONENT EXTRACTION ANALYSIS" in result
                assert "UserRegistrationProcessor" in result
                assert "EmailNotificationProcessor" in result
                assert "PaymentProcessor" in result
                assert "validateUserData" in result
                assert "validatePayment" in result
                assert "PROCESSORS TO GENERATE" in result
                assert "CRITERIA TO GENERATE" in result

    @pytest.mark.asyncio
    async def test_extract_workflow_components_summary(self, setup_method):
        """Test extraction with summary output format"""
        
        # Create test workflow
        workflow_data = {
            "states": {
                "state1": {
                    "transitions": [
                        {
                            "processors": [
                                {"name": "AgentProcessor.user_processor"}
                            ],
                            "criterion": {
                                "type": "function",
                                "function": {"name": "validateUser"}
                            }
                        }
                    ]
                }
            }
        }
        
        self.create_workflow_file("test_workflow.json", workflow_data)
        
        # Mock entity and parameters
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {"git_branch_id": "main"}
        
        params = {
            "workflow_directory": "workflow",
            "output_format": "summary"
        }
        
        # Mock get_project_file_name to return our temp directory
        with patch('tools.workflow_component_extraction_service.get_project_file_name') as mock_get_file:
            mock_get_file.return_value = self.workflow_dir
            
            # Mock repository resolver
            with patch('tools.workflow_component_extraction_service.resolve_repository_name_with_language_param') as mock_resolver:
                mock_resolver.return_value = "test-repo"
                
                # Execute extraction
                result = await self.service.extract_workflow_components("tech123", entity, **params)
                
                # Verify results
                assert "WORKFLOW COMPONENT EXTRACTION SUMMARY" in result
                assert "Total Processors Required: 1" in result
                assert "Total Criteria Required: 1" in result
                assert "UserProcessor" in result
                assert "validateUser" in result

    @pytest.mark.asyncio
    async def test_extract_workflow_components_list(self, setup_method):
        """Test extraction with list output format"""
        
        # Create test workflow
        workflow_data = {
            "states": {
                "state1": {
                    "transitions": [
                        {
                            "processors": [
                                {"name": "AgentProcessor.simple_processor"}
                            ],
                            "criterion": {
                                "type": "function",
                                "function": {"name": "simpleValidation"}
                            }
                        }
                    ]
                }
            }
        }
        
        self.create_workflow_file("test_workflow.json", workflow_data)
        
        # Mock entity and parameters
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {"git_branch_id": "main"}
        
        params = {
            "workflow_directory": "workflow",
            "output_format": "list"
        }
        
        # Mock get_project_file_name to return our temp directory
        with patch('tools.workflow_component_extraction_service.get_project_file_name') as mock_get_file:
            mock_get_file.return_value = self.workflow_dir
            
            # Mock repository resolver
            with patch('tools.workflow_component_extraction_service.resolve_repository_name_with_language_param') as mock_resolver:
                mock_resolver.return_value = "test-repo"
                
                # Execute extraction
                result = await self.service.extract_workflow_components("tech123", entity, **params)
                
                # Verify results
                assert "**PROCESSORS:**" in result
                assert "**CRITERIA:**" in result
                assert "- SimpleProcessor" in result
                assert "- simpleValidation" in result

    @pytest.mark.asyncio
    async def test_extract_workflow_components_missing_params(self, setup_method):
        """Test extraction with missing required parameters"""
        
        entity = MagicMock(spec=AgenticFlowEntity)
        
        # Missing required workflow_directory parameter
        params = {}
        
        result = await self.service.extract_workflow_components("tech123", entity, **params)
        
        # Should return error message about missing parameters
        assert "Missing required parameter" in result or "required" in result.lower()

    @pytest.mark.asyncio
    async def test_extract_workflow_components_empty_directory(self, setup_method):
        """Test extraction with empty workflow directory"""
        
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {"git_branch_id": "main"}
        
        params = {
            "workflow_directory": "workflow",
            "output_format": "summary"
        }
        
        # Mock get_project_file_name to return our empty temp directory
        with patch('tools.workflow_component_extraction_service.get_project_file_name') as mock_get_file:
            mock_get_file.return_value = self.workflow_dir
            
            # Mock repository resolver
            with patch('tools.workflow_component_extraction_service.resolve_repository_name_with_language_param') as mock_resolver:
                mock_resolver.return_value = "test-repo"
                
                # Execute extraction
                result = await self.service.extract_workflow_components("tech123", entity, **params)
                
                # Should handle empty directory gracefully
                assert "Total Processors Required: 0" in result
                assert "Total Criteria Required: 0" in result

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
    async def test_extract_from_workflow_complex(self, setup_method):
        """Test extraction from complex workflow structure"""
        
        # Create complex workflow data with nested structures
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
                        },
                        {
                            "processors": [
                                {"name": "AgentProcessor.audit_processor"}
                            ],
                            "criterion": {
                                "type": "function",
                                "function": {"name": "auditCheck"}
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
        expected_processors = {"UserRegistrationProcessor", "EmailNotificationProcessor", "AuditProcessor", "PaymentProcessor"}
        expected_criteria = {"validateUserData", "auditCheck", "validatePayment"}
        
        assert processors == expected_processors
        assert criteria == expected_criteria
