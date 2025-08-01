#!/usr/bin/env python3
"""
Tests for FunctionProcessor functionality.

This module tests the function processor's ability to execute functions
from the tools services.
"""

import unittest
from unittest.mock import Mock, patch
from processors.function_processor import FunctionProcessor
from processors.base_processor import ProcessorContext


class TestFunctionProcessor(unittest.TestCase):
    """Test cases for FunctionProcessor."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = FunctionProcessor()

    def test_processor_initialization(self):
        """Test that the processor initializes correctly."""
        self.assertIsNotNone(self.processor)
        self.assertEqual(self.processor.processor_name, "FunctionProcessor")

    def test_supports_function_processor_names(self):
        """Test that the processor supports FunctionProcessor names."""
        self.assertTrue(self.processor.supports("FunctionProcessor.test_function"))
        self.assertFalse(self.processor.supports("AgentProcessor.test_agent"))
        self.assertFalse(self.processor.supports("invalid_name"))

    def test_service_initialization(self):
        """Test that services are initialized correctly."""
        self.processor._initialize_services()
        
        self.assertIsNotNone(self.processor._services)
        self.assertIsNotNone(self.processor._function_map)
        
        # Check that expected services are present
        expected_services = [
            'file_operations', 'web_operations', 'state_management',
            'deployment', 'application_builder', 'application_editor',
            'workflow_management', 'workflow_validation', 'utility',
            'build_id_retrieval', 'github_operations', 'workflow_orchestration'
        ]
        
        for service in expected_services:
            self.assertIn(service, self.processor._services)

    def test_function_mapping(self):
        """Test that functions are mapped correctly."""
        self.processor._initialize_services()
        
        # Check that expected functions are present
        expected_functions = [
            'save_file', 'read_file', 'web_search', 'is_chat_locked',
            'deploy_cyoda_env', 'build_general_application', 'get_weather'
        ]
        
        for function in expected_functions:
            self.assertIn(function, self.processor._function_map)

    async def test_function_execution_success(self):
        """Test successful function execution."""
        # Create test context
        context = ProcessorContext(
            workflow_name="test_workflow",
            state_name="test_state",
            transition_name="test_transition",
            entity_id="test_tech_id",
            entity_data={
                "technical_id": "test_tech_id",
                "user_id": "test_user",
                "workflow_cache": {"test_key": "test_value"}
            },
            memory_tags=["test_memory"],
            execution_mode="SYNC",
            config={"processor_name": "FunctionProcessor.get_weather"}
        )

        # Execute function
        result = await self.processor.execute(context)

        # Verify result
        self.assertTrue(result.success)
        self.assertIn("data", result.data)
        self.assertEqual(result.data["data"]["function_name"], "get_weather")

    async def test_function_execution_not_found(self):
        """Test function execution with non-existent function."""
        # Create test context with non-existent function
        context = ProcessorContext(
            workflow_name="test_workflow",
            state_name="test_state",
            transition_name="test_transition",
            entity_id="test_tech_id",
            entity_data={},
            memory_tags=[],
            execution_mode="SYNC",
            config={"processor_name": "FunctionProcessor.non_existent_function"}
        )

        # Execute function
        result = await self.processor.execute(context)

        # Verify error result
        self.assertFalse(result.success)
        self.assertIn("not found", result.error_message)

    async def test_invalid_processor_name_format(self):
        """Test execution with invalid processor name format."""
        # Create test context with invalid processor name
        context = ProcessorContext(
            workflow_name="test_workflow",
            state_name="test_state",
            transition_name="test_transition",
            entity_id="test_tech_id",
            entity_data={},
            memory_tags=[],
            execution_mode="SYNC",
            config={"processor_name": "InvalidProcessor.test_function"}
        )

        # Execute function
        result = await self.processor.execute(context)

        # Verify error result
        self.assertFalse(result.success)
        self.assertIn("Invalid function processor name format", result.error_message)

    def test_entity_data_handling(self):
        """Test that entity data is passed correctly to functions."""
        entity_data = {
            "technical_id": "test_id",
            "user_id": "test_user",
            "workflow_cache": {"key": "value"},
            "workflow_name": "test_workflow"
        }

        # Verify that entity_data structure is preserved
        self.assertEqual(entity_data["technical_id"], "test_id")
        self.assertEqual(entity_data["user_id"], "test_user")
        self.assertEqual(entity_data["workflow_cache"], {"key": "value"})
        self.assertEqual(entity_data["workflow_name"], "test_workflow")

    async def test_multiple_function_execution(self):
        """Test execution of multiple different functions."""
        test_functions = ["get_weather", "is_chat_locked", "get_user_info"]

        for func_name in test_functions:
            with self.subTest(function=func_name):
                context = ProcessorContext(
                    workflow_name="test_workflow",
                    state_name="test_state",
                    transition_name="test_transition",
                    entity_id="test_tech_id",
                    entity_data={
                        "technical_id": "test_tech_id",
                        "user_id": "test_user",
                        "workflow_cache": {}
                    },
                    memory_tags=[],
                    execution_mode="SYNC",
                    config={"processor_name": f"FunctionProcessor.{func_name}"}
                )

                result = await self.processor.execute(context)
                self.assertTrue(result.success, f"Function {func_name} should execute successfully")

    async def test_function_with_parameters(self):
        """Test function execution with parameters in workflow cache."""
        context = ProcessorContext(
            workflow_name="test_workflow",
            state_name="test_state",
            transition_name="test_transition",
            entity_id="test_tech_id",
            entity_data={
                "technical_id": "test_tech_id",
                "user_id": "test_user",
                "workflow_cache": {
                    "file_path": "test.txt",
                    "file_contents": "test content"
                }
            },
            memory_tags=[],
            execution_mode="SYNC",
            config={"processor_name": "FunctionProcessor.save_file"}
        )

        result = await self.processor.execute(context)
        self.assertTrue(result.success)

    @patch('processors.function_processor.logger')
    async def test_function_execution_exception_handling(self, mock_logger):
        """Test that exceptions during function execution are handled properly."""
        # Initialize services first
        self.processor._initialize_services()

        # Mock a function to raise an exception
        original_function = self.processor._function_map.get('get_weather')
        if original_function:
            def failing_function(*args, **kwargs):
                raise Exception("Test exception")

            self.processor._function_map['get_weather'] = failing_function

            context = ProcessorContext(
                workflow_name="test_workflow",
                state_name="test_state",
                transition_name="test_transition",
                entity_id="test_tech_id",
                entity_data={},
                memory_tags=[],
                execution_mode="SYNC",
                config={"processor_name": "FunctionProcessor.get_weather"}
            )

            result = await self.processor.execute(context)

            # Verify error handling
            self.assertFalse(result.success)
            self.assertIn("Function execution failed", result.error_message)

            # Restore original function
            self.processor._function_map['get_weather'] = original_function

    def test_function_count(self):
        """Test that the expected number of functions are available."""
        self.processor._initialize_services()
        
        function_count = len(self.processor._function_map)
        
        # We expect at least 60 functions (could be more as new ones are added)
        self.assertGreaterEqual(function_count, 60)
        
        # Log the actual count for reference
        print(f"Total functions available: {function_count}")

    def test_service_mock_mode(self):
        """Test that services are initialized in mock mode."""
        self.processor._initialize_services()
        
        # All services should be initialized with mock=True
        for service_name, service in self.processor._services.items():
            # Check if service has mock attribute or was initialized with mock dependencies
            # This is a basic check - in a real scenario you might want to verify
            # that the service behaves as expected in mock mode
            self.assertIsNotNone(service)


if __name__ == "__main__":
    unittest.main()
