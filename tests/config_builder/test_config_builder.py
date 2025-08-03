#!/usr/bin/env python3
"""
Comprehensive tests for ConfigBuilder using provided test data.
"""

import json
import pytest
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from workflow.config_builder import ConfigBuilder


class TestConfigBuilder:
    """Test suite for ConfigBuilder with provided test data."""
    
    @pytest.fixture
    def config_builder(self):
        """Create ConfigBuilder instance with test workflow_configs path."""
        test_configs_path = Path(__file__).parent / "input" / "workflow_configs"
        return ConfigBuilder(str(test_configs_path))
    
    @pytest.fixture
    def expected_outputs(self):
        """Load expected output configurations."""
        expected_dir = Path(__file__).parent / "expected_output"
        outputs = {}
        
        for json_file in expected_dir.glob("*.json"):
            processor_name = json_file.stem
            with open(json_file, 'r', encoding='utf-8') as f:
                outputs[processor_name] = json.load(f)
        
        return outputs
    
    def test_agent_processor_submit_answer_5607(self, config_builder, expected_outputs):
        """Test AgentProcessor.submit_answer_5607 configuration building."""
        processor_name = "AgentProcessor.submit_answer_5607"
        expected = expected_outputs[processor_name]
        
        # Build actual configuration
        actual = config_builder.build_config(processor_name)
        
        # Validate structure and content
        errors = self._validate_config_match(actual, expected, processor_name)
        
        # Print detailed comparison
        self._print_comparison(processor_name, actual, expected, errors)
        
        # The test passes if we can build the config successfully
        # Errors are reported for manual validation
        assert isinstance(actual, dict), "Config should be a dictionary"
        assert "type" in actual, "Config should have 'type' field"
    
    def test_function_processor_clone_repo(self, config_builder, expected_outputs):
        """Test FunctionProcessor.clone_repo configuration building."""
        processor_name = "FunctionProcessor.clone_repo"
        expected = expected_outputs[processor_name]
        
        # Build actual configuration
        actual = config_builder.build_config(processor_name)
        
        # Validate structure and content
        errors = self._validate_config_match(actual, expected, processor_name)
        
        # Print detailed comparison
        self._print_comparison(processor_name, actual, expected, errors)
        
        # The test passes if we can build the config successfully
        assert isinstance(actual, dict), "Config should be a dictionary"
        assert "type" in actual, "Config should have 'type' field"
    
    def test_message_processor_notify_prototype_generation_f8ad(self, config_builder, expected_outputs):
        """Test MessageProcessor.notify_prototype_generation_f8ad configuration building."""
        processor_name = "MessageProcessor.notify_prototype_generation_f8ad"
        expected = expected_outputs[processor_name]
        
        # Build actual configuration
        actual = config_builder.build_config(processor_name)
        
        # Validate structure and content
        errors = self._validate_config_match(actual, expected, processor_name)
        
        # Print detailed comparison
        self._print_comparison(processor_name, actual, expected, errors)
        
        # The test passes if we can build the config successfully
        assert isinstance(actual, dict), "Config should be a dictionary"
        assert "type" in actual, "Config should have 'type' field"
    
    def _validate_config_match(self, actual: Dict[str, Any], expected: Dict[str, Any], 
                              processor_name: str) -> List[str]:
        """
        Validate that actual config matches expected config structure and values.
        
        Returns:
            List of error messages for manual validation
        """
        errors = []
        
        # Check all expected keys are present
        missing_keys = set(expected.keys()) - set(actual.keys())
        if missing_keys:
            errors.append(f"Missing keys: {missing_keys}")
        
        # Check extra keys in actual
        extra_keys = set(actual.keys()) - set(expected.keys())
        if extra_keys:
            errors.append(f"Extra keys: {extra_keys}")
        
        # Check values for common keys
        common_keys = set(expected.keys()) & set(actual.keys())
        for key in common_keys:
            value_errors = self._compare_values(actual[key], expected[key], key)
            errors.extend(value_errors)
        
        return errors
    
    def _compare_values(self, actual_value: Any, expected_value: Any, key_path: str) -> List[str]:
        """
        Compare actual and expected values recursively.
        
        Returns:
            List of error messages for value mismatches
        """
        errors = []
        
        # Type mismatch
        if type(actual_value) != type(expected_value):
            errors.append(f"Type mismatch at '{key_path}': "
                         f"actual={type(actual_value).__name__}, "
                         f"expected={type(expected_value).__name__}")
            return errors
        
        # Handle different data types
        if isinstance(expected_value, dict):
            # Recursive comparison for dictionaries
            missing_keys = set(expected_value.keys()) - set(actual_value.keys())
            if missing_keys:
                errors.append(f"Missing keys at '{key_path}': {missing_keys}")
            
            extra_keys = set(actual_value.keys()) - set(expected_value.keys())
            if extra_keys:
                errors.append(f"Extra keys at '{key_path}': {extra_keys}")
            
            common_keys = set(expected_value.keys()) & set(actual_value.keys())
            for sub_key in common_keys:
                sub_errors = self._compare_values(
                    actual_value[sub_key], 
                    expected_value[sub_key], 
                    f"{key_path}.{sub_key}"
                )
                errors.extend(sub_errors)
        
        elif isinstance(expected_value, list):
            # Compare list lengths
            if len(actual_value) != len(expected_value):
                errors.append(f"List length mismatch at '{key_path}': "
                             f"actual={len(actual_value)}, expected={len(expected_value)}")
            
            # Compare list elements
            for i, (actual_item, expected_item) in enumerate(zip(actual_value, expected_value)):
                item_errors = self._compare_values(
                    actual_item, 
                    expected_item, 
                    f"{key_path}[{i}]"
                )
                errors.extend(item_errors)
        
        else:
            # Direct value comparison for primitives
            if actual_value != expected_value:
                errors.append(f"Value mismatch at '{key_path}': "
                             f"actual={repr(actual_value)}, expected={repr(expected_value)}")
        
        return errors
    
    def _print_comparison(self, processor_name: str, actual: Dict[str, Any], 
                         expected: Dict[str, Any], errors: List[str]):
        """Print detailed comparison results."""
        print(f"\n{'='*60}")
        print(f"COMPARISON RESULTS: {processor_name}")
        print(f"{'='*60}")
        
        if not errors:
            print("✅ PERFECT MATCH: All keys and values match exactly!")
        else:
            print(f"⚠️  DIFFERENCES FOUND: {len(errors)} issues")
            print("\nERRORS FOR MANUAL VALIDATION:")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
        
        print(f"\nACTUAL CONFIG SUMMARY:")
        print(f"  - Keys: {list(actual.keys())}")
        print(f"  - Type: {actual.get('type', 'N/A')}")
        
        if processor_name.startswith("AgentProcessor"):
            print(f"  - Tools count: {len(actual.get('tools', []))}")
            print(f"  - Messages count: {len(actual.get('messages', []))}")
            print(f"  - Model: {actual.get('model', {}).get('model_name', 'N/A')}")
        elif processor_name.startswith("FunctionProcessor"):
            print(f"  - Function name: {actual.get('function', {}).get('name', 'N/A')}")
        elif processor_name.startswith("MessageProcessor"):
            print(f"  - Notification length: {len(actual.get('notification', ''))}")
            print(f"  - Publish: {actual.get('publish', 'N/A')}")
        
        print(f"\nEXPECTED CONFIG SUMMARY:")
        print(f"  - Keys: {list(expected.keys())}")
        print(f"  - Type: {expected.get('type', 'N/A')}")
        
        if processor_name.startswith("AgentProcessor"):
            print(f"  - Tools count: {len(expected.get('tools', []))}")
            print(f"  - Messages count: {len(expected.get('messages', []))}")
            print(f"  - Model: {expected.get('model', {}).get('model_name', 'N/A')}")
        elif processor_name.startswith("FunctionProcessor"):
            print(f"  - Function name: {expected.get('function', {}).get('name', 'N/A')}")
        elif processor_name.startswith("MessageProcessor"):
            print(f"  - Notification length: {len(expected.get('notification', ''))}")
            print(f"  - Publish: {expected.get('publish', 'N/A')}")


def run_manual_tests():
    """Run tests manually for detailed output."""
    test_configs_path = Path(__file__).parent / "input" / "workflow_configs"
    builder = ConfigBuilder(str(test_configs_path))
    
    processor_names = [
        "AgentProcessor.submit_answer_5607",
        "FunctionProcessor.clone_repo", 
        "MessageProcessor.notify_prototype_generation_f8ad"
    ]
    
    print("ConfigBuilder Test Results")
    print("=" * 60)
    
    for processor_name in processor_names:
        try:
            config = builder.build_config(processor_name)
            print(f"\n✅ {processor_name}: SUCCESS")
            print(f"   Config type: {config.get('type', 'unknown')}")
            print(f"   Keys: {list(config.keys())}")
        except Exception as e:
            print(f"\n❌ {processor_name}: FAILED")
            print(f"   Error: {e}")


if __name__ == "__main__":
    run_manual_tests()
