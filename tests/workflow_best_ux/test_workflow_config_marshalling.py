"""
Test Workflow Configuration Marshalling

Tests that workflow.py files can be marshalled into their config JSON automatically.
"""

import pytest
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from workflow_best_ux.workflows.simple_chat_workflow.workflow import simple_chat_workflow


class TestWorkflowConfigMarshalling:
    """Test workflow configuration marshalling to JSON"""
    
    def test_workflow_function_exists(self):
        """Test that workflow function exists and is callable"""
        assert callable(simple_chat_workflow), "Workflow function must be callable"
    
    def test_workflow_returns_dict(self):
        """Test that workflow function returns a dictionary"""
        workflow_config = simple_chat_workflow()
        assert isinstance(workflow_config, dict), "Workflow must return dict"
    
    def test_workflow_has_required_properties(self):
        """Test that workflow has all required properties for JSON marshalling"""
        workflow_config = simple_chat_workflow()
        
        # Check required properties exist (using new field names)
        required_props = ["name", "desc", "initialState", "states"]
        for prop in required_props:
            assert prop in workflow_config, f"Workflow must have {prop} property"

        # Check property types
        assert isinstance(workflow_config["name"], str), "Name must be string"
        assert isinstance(workflow_config["desc"], str), "Description must be string"
        assert isinstance(workflow_config["initialState"], str), "Initial state must be string"
        assert isinstance(workflow_config["states"], dict), "States must be dict"
    
    def test_workflow_states_structure(self):
        """Test that workflow states have correct structure"""
        workflow_config = simple_chat_workflow()
        states = workflow_config["states"]
        
        # Check that states exist
        assert len(states) > 0, "Workflow must have at least one state"
        
        # Check each state structure
        for state_name, state_config in states.items():
            assert isinstance(state_name, str), f"State name {state_name} must be string"
            assert isinstance(state_config, dict), f"State {state_name} config must be dict"
            
            # Check state properties
            if "description" in state_config:
                assert isinstance(state_config["description"], str), f"State {state_name} description must be string"
            
            if "transitions" in state_config:
                assert isinstance(state_config["transitions"], list), f"State {state_name} transitions must be list"
                
                # Check each transition
                for transition in state_config["transitions"]:
                    assert isinstance(transition, dict), f"Transition in state {state_name} must be dict"
                    
                    # Check transition properties
                    required_transition_props = ["name", "next", "manual"]
                    for prop in required_transition_props:
                        assert prop in transition, f"Transition must have {prop} property"
                    
                    assert isinstance(transition["name"], str), "Transition name must be string"
                    assert isinstance(transition["next"], str), "Transition next must be string"
                    assert isinstance(transition["manual"], bool), "Transition manual must be bool"
                    
                    # Check processors if they exist
                    if "processors" in transition:
                        assert isinstance(transition["processors"], list), "Processors must be list"
                        
                        for processor in transition["processors"]:
                            assert isinstance(processor, dict), "Processor must be dict"
                            assert "name" in processor, "Processor must have name"
                            assert isinstance(processor["name"], str), "Processor name must be string"
    
    def test_workflow_criterion_structure(self):
        """Test that workflow criterion has correct structure"""
        workflow_config = simple_chat_workflow()
        
        if "criterion" in workflow_config and workflow_config["criterion"]:
            criterion = workflow_config["criterion"]
            assert isinstance(criterion, dict), "Criterion must be dict"

            # Check criterion properties (using new field names)
            required_criterion_props = ["jsonPath", "operation", "value"]
            for prop in required_criterion_props:
                assert prop in criterion, f"Criterion must have {prop} property"

            assert isinstance(criterion["jsonPath"], str), "Criterion jsonPath must be string"
            assert isinstance(criterion["operation"], str), "Criterion operation must be string"
            assert isinstance(criterion["value"], str), "Criterion value must be string"
    
    def test_workflow_can_be_marshalled_to_json(self):
        """Test that workflow can be converted to JSON"""
        workflow_config = simple_chat_workflow()
        
        # Convert to JSON
        json_str = json.dumps(workflow_config, indent=2)
        
        # Verify JSON is valid
        assert isinstance(json_str, str), "JSON must be string"
        
        # Parse back to verify structure
        parsed = json.loads(json_str)
        assert parsed == workflow_config, "JSON round-trip must preserve data"
    
    def test_workflow_processor_references(self):
        """Test that workflow processor references use correct naming"""
        workflow_config = simple_chat_workflow()
        states = workflow_config["states"]
        
        # Collect all processor names
        processor_names = []
        for state_name, state_config in states.items():
            if "transitions" in state_config:
                for transition in state_config["transitions"]:
                    if "processors" in transition:
                        for processor in transition["processors"]:
                            processor_names.append(processor["name"])
        
        # Check processor naming patterns
        for processor_name in processor_names:
            assert isinstance(processor_name, str), "Processor name must be string"
            
            # Check that processor names follow expected patterns
            valid_prefixes = ["AgentProcessor.", "MessageProcessor.", "FunctionProcessor."]
            has_valid_prefix = any(processor_name.startswith(prefix) for prefix in valid_prefixes)
            assert has_valid_prefix, f"Processor {processor_name} must have valid prefix"
    
    def test_workflow_marshalling_integration(self):
        """Integration test for complete workflow config marshalling"""
        workflow_config = simple_chat_workflow()
        
        # Create complete JSON representation
        workflow_json = {
            "type": "workflow",
            "config": workflow_config
        }
        
        # Convert to JSON and verify
        json_str = json.dumps(workflow_json, indent=2)
        parsed = json.loads(json_str)
        
        # Verify structure
        assert parsed["type"] == "workflow"
        assert "config" in parsed
        assert parsed["config"] == workflow_config
        
        print("✅ Workflow config marshalling test passed!")
        print(f"Generated JSON:\n{json_str}")
    
    def test_workflow_specific_properties(self):
        """Test specific properties of the simple chat workflow"""
        workflow_config = simple_chat_workflow()
        
        # Check specific workflow properties
        assert workflow_config["name"] == "simple_chat_workflow", "Workflow name must be correct"
        assert workflow_config["initialState"] == "none", "Initial state must be 'none'"
        
        # Check that expected states exist
        expected_states = ["none", "ready", "processing"]
        states = workflow_config["states"]
        for expected_state in expected_states:
            assert expected_state in states, f"State {expected_state} must exist"
    
    def test_workflow_builder_usage(self):
        """Test that workflow uses the builder pattern correctly"""
        # This test verifies that the workflow function uses the builder
        # by checking the structure of the returned configuration
        workflow_config = simple_chat_workflow()
        
        # The workflow should be built using the WorkflowBuilder
        # which produces a specific structure
        assert "name" in workflow_config, "Builder must set name"
        assert "desc" in workflow_config, "Builder must set desc"
        assert "initialState" in workflow_config, "Builder must set initialState"
        assert "states" in workflow_config, "Builder must set states"
        
        # Check that the structure matches what WorkflowBuilder produces
        assert "name" in workflow_config, "Builder must set name"
        assert "desc" in workflow_config, "Builder must set desc"
        assert "initialState" in workflow_config, "Builder must set initialState"
        assert "states" in workflow_config, "Builder must set states"

        # Check that transitions have the correct structure
        for state_name, state_config in workflow_config["states"].items():
            if "transitions" in state_config:
                for transition in state_config["transitions"]:
                    # Check that transitions have the structure produced by TransitionBuilder
                    assert "name" in transition, "TransitionBuilder must set name"
                    assert "next" in transition, "TransitionBuilder must set next"
                    assert "manual" in transition, "TransitionBuilder must set manual"


if __name__ == "__main__":
    test = TestWorkflowConfigMarshalling()
    test.test_workflow_function_exists()
    test.test_workflow_returns_dict()
    test.test_workflow_has_required_properties()
    test.test_workflow_states_structure()
    test.test_workflow_criterion_structure()
    test.test_workflow_can_be_marshalled_to_json()
    test.test_workflow_processor_references()
    test.test_workflow_marshalling_integration()
    test.test_workflow_specific_properties()
    test.test_workflow_builder_usage()
    print("🎉 All workflow config marshalling tests passed!")
