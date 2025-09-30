import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from entity.chat.workflow import ChatWorkflow
from entity.model import AgenticFlowEntity
import common.config.const as const


class TestWorkflowOrchestratorIntegration:
    """Integration tests for workflow orchestrator tool in ChatWorkflow."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for ChatWorkflow."""
        return {
            'dataset': None,
            'workflow_helper_service': AsyncMock(),
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
            'workflow_converter_service': AsyncMock(),
            'scheduler_service': AsyncMock(),
            'data_service': AsyncMock(),
            'mock': True
        }

    @pytest.fixture
    def chat_workflow(self, mock_dependencies):
        """Create ChatWorkflow instance."""
        return ChatWorkflow(**mock_dependencies)

    @pytest.fixture
    def mock_agentic_entity(self):
        """Create mock AgenticFlowEntity."""
        entity = MagicMock(spec=AgenticFlowEntity)
        entity.workflow_cache = {
            const.GIT_BRANCH_PARAM: "test_branch",
            const.REPOSITORY_NAME_PARAM: "java-client-template"
        }
        entity.workflow_name = "test_workflow"
        entity.failed = False
        entity.error = None
        return entity

    @pytest.fixture
    def sample_workflow_json(self):
        """Create sample workflow JSON for testing."""
        return {
            "version": "1.0",
            "name": "Order Workflow",
            "desc": "Workflow for Order entity managing order processing",
            "initialState": "created",
            "active": True,
            "states": {
                "created": {
                    "transitions": [
                        {
                            "name": "validate_order",
                            "next": "validated",
                            "manual": False,
                            "processors": [
                                {
                                    "name": "OrderValidationProcessor",
                                    "executionMode": "SYNC",
                                    "config": {
                                        "calculationNodesTags": "cyoda_application"
                                    }
                                }
                            ]
                        }
                    ]
                },
                "validated": {
                    "transitions": [
                        {
                            "name": "process_payment",
                            "next": "paid",
                            "manual": False,
                            "criterion": {
                                "type": "function",
                                "function": {
                                    "name": "PaymentSuccessCriterion",
                                    "config": {
                                        "calculationNodesTags": "cyoda_application"
                                    }
                                }
                            },
                            "processors": [
                                {
                                    "name": "PaymentProcessor",
                                    "executionMode": "SYNC",
                                    "config": {
                                        "calculationNodesTags": "cyoda_application"
                                    }
                                }
                            ]
                        }
                    ]
                },
                "paid": {
                    "transitions": [
                        {
                            "name": "fulfill_order",
                            "next": "fulfilled",
                            "manual": False,
                            "processors": [
                                {
                                    "name": "FulfillmentProcessor",
                                    "executionMode": "ASYNC",
                                    "config": {
                                        "calculationNodesTags": "cyoda_application"
                                    }
                                }
                            ]
                        }
                    ]
                },
                "fulfilled": {
                    "transitions": []
                }
            }
        }

    def test_function_registry_contains_generate_workflow_orchestrators(self, chat_workflow):
        """Test that the function registry contains the generate_workflow_orchestrators function."""
        assert hasattr(chat_workflow, '_function_registry')
        assert 'generate_workflow_orchestrators' in chat_workflow._function_registry
        
        # Test that the function can be accessed via getattr
        func = getattr(chat_workflow, 'generate_workflow_orchestrators')
        assert callable(func)

    @pytest.mark.asyncio
    async def test_generate_workflow_orchestrators_via_registry(self, chat_workflow, mock_agentic_entity, sample_workflow_json):
        """Test calling generate_workflow_orchestrators through the function registry."""
        params = {"workflow_directory_path": "src/main/java/com/java_template/application/workflow"}
        
        # Mock file system operations
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['Order.json']), \
             patch('builtins.open', mock_open(read_data=json.dumps(sample_workflow_json))), \
             patch('tools.workflow_orchestrator_service._save_file', new_callable=AsyncMock) as mock_save:
            
            # Call through the function registry
            result = await chat_workflow.generate_workflow_orchestrators(
                technical_id="test_123",
                entity=mock_agentic_entity,
                **params
            )
            
            # Verify success
            assert "Successfully generated 1 workflow orchestrators" in result
            
            # Verify the orchestrator was saved
            mock_save.assert_called_once()
            call_args = mock_save.call_args
            
            # Check the saved file path
            assert call_args[1]['item'] == "src/main/java/com/java_template/application/orchestrator/OrderWorkflowOrchestrator.java"
            
            # Check the generated code content
            generated_code = call_args[1]['_data']
            assert "public class OrderWorkflowOrchestrator" in generated_code
            assert "validate_order" in generated_code
            assert "OrderValidationProcessor" in generated_code
            assert "PaymentProcessor" in generated_code
            assert "PaymentSuccessCriterion" in generated_code

    @pytest.mark.asyncio
    async def test_generate_workflow_orchestrators_multiple_entities(self, chat_workflow, mock_agentic_entity):
        """Test generating orchestrators for multiple entities."""
        params = {"workflow_directory_path": "src/main/java/com/java_template/application/workflow"}
        
        # Create different workflow JSONs for different entities
        order_workflow = {
            "states": {
                "created": {
                    "transitions": [
                        {
                            "name": "validate",
                            "next": "validated",
                            "processors": [{"name": "OrderValidator"}]
                        }
                    ]
                }
            }
        }
        
        user_workflow = {
            "states": {
                "registered": {
                    "transitions": [
                        {
                            "name": "activate",
                            "next": "active",
                            "processors": [{"name": "UserActivator"}]
                        }
                    ]
                }
            }
        }
        
        # Mock file system to return different content for different files
        def mock_open_side_effect(file_path, *args, **kwargs):
            if 'Order.json' in file_path:
                return mock_open(read_data=json.dumps(order_workflow)).return_value
            elif 'User.json' in file_path:
                return mock_open(read_data=json.dumps(user_workflow)).return_value
            else:
                return mock_open(read_data='{}').return_value
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['Order.json', 'User.json']), \
             patch('builtins.open', side_effect=mock_open_side_effect), \
             patch('tools.workflow_orchestrator_service._save_file', new_callable=AsyncMock) as mock_save:
            
            result = await chat_workflow.generate_workflow_orchestrators(
                technical_id="test_123",
                entity=mock_agentic_entity,
                **params
            )
            
            # Verify both orchestrators were generated
            assert "Successfully generated 2 workflow orchestrators" in result
            assert mock_save.call_count == 2
            
            # Verify the correct files were saved
            saved_files = [call[1]['item'] for call in mock_save.call_args_list]
            expected_files = [
                "src/main/java/com/java_template/application/orchestrator/OrderWorkflowOrchestrator.java",
                "src/main/java/com/java_template/application/orchestrator/UserWorkflowOrchestrator.java"
            ]
            
            for expected_file in expected_files:
                assert expected_file in saved_files

    @pytest.mark.asyncio
    async def test_generate_workflow_orchestrators_error_handling(self, chat_workflow, mock_agentic_entity):
        """Test error handling in the integrated function."""
        params = {"workflow_directory_path": "src/main/java/com/java_template/application/workflow"}
        
        # Mock an exception during file operations
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['Job.json']), \
             patch('builtins.open', mock_open(read_data='{"states": {}}')), \
             patch('tools.workflow_orchestrator_service._save_file', side_effect=Exception("Save file error")):

            result = await chat_workflow.generate_workflow_orchestrators(
                technical_id="test_123",
                entity=mock_agentic_entity,
                **params
            )

            # Verify error is handled gracefully
            assert "Error generating workflow orchestrators" in result
            assert mock_agentic_entity.failed is True

    def test_workflow_orchestrator_service_initialization(self, chat_workflow):
        """Test that WorkflowOrchestratorService is properly initialized."""
        assert hasattr(chat_workflow, 'workflow_orchestrator_service')
        assert chat_workflow.workflow_orchestrator_service is not None
        
        # Verify the service has the expected dependencies
        service = chat_workflow.workflow_orchestrator_service
        assert hasattr(service, 'workflow_helper_service')
        assert hasattr(service, 'entity_service')
        assert hasattr(service, 'cyoda_auth_service')

    @pytest.mark.asyncio
    async def test_missing_required_parameters(self, chat_workflow, mock_agentic_entity):
        """Test error handling for missing required parameters."""
        # Call without required workflow_directory_path parameter
        result = await chat_workflow.generate_workflow_orchestrators(
            technical_id="test_123",
            entity=mock_agentic_entity
        )
        
        assert "Missing required parameter" in result

    @pytest.mark.asyncio
    async def test_empty_workflow_directory(self, chat_workflow, mock_agentic_entity):
        """Test handling of empty workflow directory."""
        params = {"workflow_directory_path": "src/main/java/com/java_template/application/workflow"}
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=[]):
            
            result = await chat_workflow.generate_workflow_orchestrators(
                technical_id="test_123",
                entity=mock_agentic_entity,
                **params
            )
            
            assert "No workflow JSON files found" in result
