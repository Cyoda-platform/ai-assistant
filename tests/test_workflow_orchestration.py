#!/usr/bin/env python3
"""
Tests for WorkflowOrchestrationService functionality.

This module tests the workflow orchestration service that replaced
the legacy WorkflowHelperService.
"""

import json
import tempfile
import unittest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from tools.workflow_orchestration_service import WorkflowOrchestrationService
from entity.chat.chat import ChatEntity


class TestWorkflowOrchestrationService(unittest.TestCase):
    """Test cases for WorkflowOrchestrationService."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_workflow_helper = Mock()
        self.mock_entity_service = AsyncMock()
        self.mock_cyoda_auth = Mock()
        self.mock_workflow_converter = Mock()
        self.mock_scheduler = Mock()
        self.mock_data_service = Mock()
        self.mock_dataset = Mock()

        # Create service instance
        self.service = WorkflowOrchestrationService(
            workflow_helper_service=self.mock_workflow_helper,
            entity_service=self.mock_entity_service,
            cyoda_auth_service=self.mock_cyoda_auth,
            workflow_converter_service=self.mock_workflow_converter,
            scheduler_service=self.mock_scheduler,
            data_service=self.mock_data_service,
            dataset=self.mock_dataset,
            mock=True
        )

    def test_service_initialization(self):
        """Test that the service initializes correctly."""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.workflow_helper_service, self.mock_workflow_helper)
        self.assertEqual(self.service.entity_service, self.mock_entity_service)

    async def test_launch_agentic_workflow(self):
        """Test launching an agentic workflow."""
        # Setup mock entity
        mock_entity = Mock()
        mock_entity.user_id = "test_user"
        mock_entity.questions_queue_id = "queue_123"
        mock_entity.memory_id = "memory_123"

        # Setup mock entity service
        self.mock_entity_service.add_item.return_value = "child_tech_id_123"

        # Test workflow launch
        result = await self.service.launch_agentic_workflow(
            technical_id="parent_tech_id",
            entity=mock_entity,
            entity_model="ChatEntity",
            workflow_name="test_workflow",
            user_request="Test request",
            workflow_cache={"key": "value"}
        )

        # Verify result
        self.assertEqual(result, "child_tech_id_123")
        
        # Verify entity service was called
        self.mock_entity_service.add_item.assert_called_once()
        call_args = self.mock_entity_service.add_item.call_args
        
        self.assertEqual(call_args.kwargs["entity_model"], "ChatEntity")
        self.assertIsInstance(call_args.kwargs["entity"], ChatEntity)

    async def test_launch_scheduled_workflow(self):
        """Test launching a scheduled workflow."""
        # Setup mock entity service
        self.mock_entity_service.add_item.return_value = "scheduler_tech_id_123"

        # Test scheduled workflow launch
        result = await self.service.launch_scheduled_workflow(
            awaited_entity_ids=["entity1", "entity2"],
            triggered_entity_id="trigger_entity",
            triggered_entity_next_transition="next_transition"
        )

        # Verify result
        self.assertEqual(result, "scheduler_tech_id_123")
        
        # Verify entity service was called
        self.mock_entity_service.add_item.assert_called_once()

    async def test_order_states_in_fsm(self):
        """Test ordering states in a finite state machine."""
        # Create test FSM
        test_fsm = {
            "initialState": "start",
            "states": {
                "start": {
                    "transitions": [
                        {"next": "middle"}
                    ]
                },
                "middle": {
                    "transitions": [
                        {"next": "end"}
                    ]
                },
                "end": {
                    "transitions": []
                },
                "orphan": {
                    "transitions": []
                }
            }
        }

        # Test ordering
        ordered_fsm = await self.service.order_states_in_fsm(test_fsm)

        # Verify ordering
        state_names = list(ordered_fsm["states"].keys())
        self.assertEqual(state_names[0], "start")  # Initial state first
        self.assertEqual(state_names[1], "middle")  # Connected state second
        self.assertEqual(state_names[2], "end")     # Final state third
        self.assertEqual(state_names[3], "orphan")  # Orphan state last

    async def test_read_json(self):
        """Test reading JSON from file."""
        # Create temporary JSON file
        test_data = {"key": "value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            # Test reading
            result = await self.service.read_json(temp_file)
            
            # Verify result
            self.assertEqual(result, test_data)
        finally:
            # Clean up
            Path(temp_file).unlink()

    @patch('tools.workflow_orchestration_service._save_file')
    async def test_persist_json(self, mock_save_file):
        """Test persisting JSON data."""
        # Test data
        test_data = {"workflow": "test", "version": "1.0"}
        
        # Test persistence
        await self.service.persist_json(
            path_or_item="test_workflow.json",
            data=test_data,
            git_branch_id="main",
            repository_name="test_repo"
        )

        # Verify save_file was called
        mock_save_file.assert_called_once()
        call_args = mock_save_file.call_args
        
        # Verify JSON serialization
        saved_data = call_args.kwargs["_data"]
        self.assertIsInstance(saved_data, str)
        parsed_data = json.loads(saved_data)
        self.assertEqual(parsed_data, test_data)

    def test_mock_data_loading(self):
        """Test loading of mock data in mock mode."""
        # The service should handle missing mock data gracefully
        self.assertIsNotNone(self.service)
        
        # In mock mode, json_mock_data should be empty dict if file doesn't exist
        if hasattr(self.service, 'json_mock_data'):
            self.assertIsInstance(self.service.json_mock_data, dict)

    async def test_launch_agentic_workflow_without_user_request(self):
        """Test launching workflow without user request."""
        # Setup mock entity
        mock_entity = Mock()
        mock_entity.user_id = "test_user"
        mock_entity.questions_queue_id = "queue_123"
        mock_entity.memory_id = "memory_123"

        # Setup mock entity service
        self.mock_entity_service.add_item.return_value = "child_tech_id_123"

        # Test workflow launch without user request
        result = await self.service.launch_agentic_workflow(
            technical_id="parent_tech_id",
            entity=mock_entity,
            entity_model="ChatEntity",
            workflow_name="test_workflow"
        )

        # Verify result
        self.assertEqual(result, "child_tech_id_123")

    async def test_launch_agentic_workflow_with_edge_messages(self):
        """Test launching workflow with edge messages store."""
        # Setup mock entity
        mock_entity = Mock()
        mock_entity.user_id = "test_user"
        mock_entity.questions_queue_id = "queue_123"
        mock_entity.memory_id = "memory_123"

        # Setup mock entity service
        self.mock_entity_service.add_item.return_value = "child_tech_id_123"

        # Test workflow launch with edge messages
        edge_messages = {"message1": "content1"}
        result = await self.service.launch_agentic_workflow(
            technical_id="parent_tech_id",
            entity=mock_entity,
            entity_model="ChatEntity",
            workflow_name="test_workflow",
            edge_messages_store=edge_messages
        )

        # Verify result
        self.assertEqual(result, "child_tech_id_123")

    def test_backward_compatibility_alias(self):
        """Test that WorkflowHelperService alias works."""
        from tools.workflow_orchestration_service import WorkflowHelperService
        
        # Verify alias points to the same class
        self.assertEqual(WorkflowHelperService, WorkflowOrchestrationService)

    async def test_complex_fsm_ordering(self):
        """Test ordering of a complex FSM with multiple branches."""
        complex_fsm = {
            "initialState": "init",
            "states": {
                "init": {
                    "transitions": [
                        {"next": "branch1"},
                        {"next": "branch2"}
                    ]
                },
                "branch1": {
                    "transitions": [
                        {"next": "merge"}
                    ]
                },
                "branch2": {
                    "transitions": [
                        {"next": "merge"}
                    ]
                },
                "merge": {
                    "transitions": [
                        {"next": "final"}
                    ]
                },
                "final": {
                    "transitions": []
                },
                "unreachable": {
                    "transitions": []
                }
            }
        }

        # Test ordering
        ordered_fsm = await self.service.order_states_in_fsm(complex_fsm)

        # Verify initial state is first
        state_names = list(ordered_fsm["states"].keys())
        self.assertEqual(state_names[0], "init")
        
        # Verify unreachable state is last
        self.assertEqual(state_names[-1], "unreachable")
        
        # Verify all states are present
        self.assertEqual(len(state_names), len(complex_fsm["states"]))


if __name__ == "__main__":
    # Run async tests
    import asyncio
    
    class AsyncTestRunner:
        def run_async_tests(self):
            # Get all test methods
            suite = unittest.TestLoader().loadTestsFromTestCase(TestWorkflowOrchestrationService)
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            return result.wasSuccessful()

    # For async tests, we need to run them in an event loop
    if __name__ == "__main__":
        unittest.main()
