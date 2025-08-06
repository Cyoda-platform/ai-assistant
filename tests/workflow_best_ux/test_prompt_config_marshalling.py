"""
Test Prompt Configuration Marshalling

Tests that prompt.py files can be marshalled into their config JSON automatically.
"""

import pytest
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from workflow_best_ux.prompts.assistant_prompt.prompt import AssistantPrompt


class TestPromptConfigMarshalling:
    """Test prompt configuration marshalling to JSON"""
    
    def test_prompt_has_get_config_method(self):
        """Test that prompt has get_config method"""
        prompt = AssistantPrompt()
        assert hasattr(prompt, 'get_config'), "Prompt must have get_config method"
        assert callable(prompt.get_config), "get_config must be callable"
    
    def test_prompt_get_config_returns_prompt_config(self):
        """Test that get_config returns PromptConfig interface"""
        prompt = AssistantPrompt()
        config = prompt.get_config()
        
        # Check that it implements PromptConfig interface
        assert hasattr(config, 'get_name'), "Config must have get_name method"
        assert hasattr(config, 'get_content'), "Config must have get_content method"
        assert callable(config.get_name), "get_name must be callable"
        assert callable(config.get_content), "get_content must be callable"
    
    def test_prompt_config_has_required_properties(self):
        """Test that prompt config has all required properties for JSON marshalling"""
        prompt = AssistantPrompt()
        config = prompt.get_config()
        
        # Check required properties exist
        assert hasattr(config, 'variables'), "Config must have variables"
        
        # Check properties have correct types
        assert isinstance(config.variables, dict), "Variables must be dict"
        
        # Check content
        content = config.get_content()
        assert isinstance(content, str), "Content must be string"
    
    def test_prompt_config_can_be_marshalled_to_dict(self):
        """Test that prompt config can be converted to dictionary"""
        prompt = AssistantPrompt()
        config = prompt.get_config()
        
        # Create dictionary representation
        config_dict = {
            "name": AssistantPrompt.get_name(),
            "content": config.get_content(),
            "variables": config.variables
        }
        
        # Verify dictionary structure
        assert isinstance(config_dict, dict), "Config must be convertible to dict"
        assert "name" in config_dict, "Config dict must have name"
        assert "content" in config_dict, "Config dict must have content"
        assert "variables" in config_dict, "Config dict must have variables"
        
        # Verify values
        assert config_dict["name"] == "assistant_prompt", "Name must match get_name()"
        assert isinstance(config_dict["content"], str), "Content must be string"
        assert isinstance(config_dict["variables"], dict), "Variables must be dict"
    
    def test_prompt_config_can_be_marshalled_to_json(self):
        """Test that prompt config can be converted to JSON"""
        prompt = AssistantPrompt()
        config = prompt.get_config()
        
        # Create JSON representation
        config_dict = {
            "name": AssistantPrompt.get_name(),
            "content": config.get_content(),
            "variables": config.variables
        }
        
        # Convert to JSON
        json_str = json.dumps(config_dict, indent=2)
        
        # Verify JSON is valid
        assert isinstance(json_str, str), "JSON must be string"
        
        # Parse back to verify structure
        parsed = json.loads(json_str)
        assert parsed == config_dict, "JSON round-trip must preserve data"
    
    def test_prompt_static_get_name_method(self):
        """Test that prompt has static get_name method"""
        # Test static method exists
        assert hasattr(AssistantPrompt, 'get_name'), "Prompt must have static get_name method"
        assert callable(AssistantPrompt.get_name), "get_name must be callable"
        
        # Test static method returns correct name
        name = AssistantPrompt.get_name()
        assert isinstance(name, str), "get_name must return string"
        assert name == "assistant_prompt", "get_name must return correct name"
    
    def test_prompt_content_loading(self):
        """Test that prompt can load content from markdown file"""
        prompt = AssistantPrompt()
        content = prompt.read_content()
        
        # Content should be loaded (either from file or default)
        assert isinstance(content, str), "Content must be string"
        assert len(content) > 0, "Content must not be empty"
    
    def test_prompt_variable_substitution(self):
        """Test that prompt can perform variable substitution"""
        prompt = AssistantPrompt()
        
        # Test with variables
        variables = {
            "platform_name": "TestPlatform",
            "supported_languages": "Python, Java, JavaScript"
        }
        
        rendered = prompt.render_content(variables)
        
        # Check that content is rendered
        assert isinstance(rendered, str), "Rendered content must be string"
        assert len(rendered) > 0, "Rendered content must not be empty"
        
        # Check that variables are substituted (if template contains them)
        if "{platform_name}" in prompt.read_content():
            assert "TestPlatform" in rendered, "Platform name should be substituted"
    
    def test_prompt_config_marshalling_integration(self):
        """Integration test for complete prompt config marshalling"""
        prompt = AssistantPrompt()
        
        # Get configuration
        config = prompt.get_config()
        
        # Create complete JSON representation
        prompt_json = {
            "type": "prompt",
            "name": prompt.get_name(),
            "config": {
                "content": config.get_content(),
                "variables": config.variables
            }
        }
        
        # Convert to JSON and verify
        json_str = json.dumps(prompt_json, indent=2)
        parsed = json.loads(json_str)
        
        # Verify structure
        assert parsed["type"] == "prompt"
        assert parsed["name"] == "assistant_prompt"
        assert "config" in parsed
        assert "content" in parsed["config"]
        assert "variables" in parsed["config"]
        
        print("✅ Prompt config marshalling test passed!")
        print(f"Generated JSON:\n{json_str}")
    
    def test_prompt_aiconfig_interface(self):
        """Test that prompt implements AIConfig interface"""
        prompt = AssistantPrompt()
        
        # Check AIConfig interface
        assert hasattr(prompt, 'get_name'), "Prompt must have get_name method"
        assert callable(prompt.get_name), "get_name must be callable"
        
        # Check get_config method
        assert hasattr(prompt, 'get_config'), "Prompt must have get_config method"
        assert callable(prompt.get_config), "get_config must be callable"
    
    def test_prompt_variables_structure(self):
        """Test that prompt variables have correct structure"""
        prompt = AssistantPrompt()
        config = prompt.get_config()
        
        # Check variables structure
        variables = config.variables
        assert isinstance(variables, dict), "Variables must be dict"
        
        # Check that common variables exist
        expected_vars = ["platform_name", "supported_languages"]
        for var in expected_vars:
            if var in variables:
                assert isinstance(variables[var], str), f"Variable {var} must be string"


if __name__ == "__main__":
    test = TestPromptConfigMarshalling()
    test.test_prompt_has_get_config_method()
    test.test_prompt_get_config_returns_prompt_config()
    test.test_prompt_config_has_required_properties()
    test.test_prompt_config_can_be_marshalled_to_dict()
    test.test_prompt_config_can_be_marshalled_to_json()
    test.test_prompt_static_get_name_method()
    test.test_prompt_content_loading()
    test.test_prompt_variable_substitution()
    test.test_prompt_config_marshalling_integration()
    test.test_prompt_aiconfig_interface()
    test.test_prompt_variables_structure()
    print("🎉 All prompt config marshalling tests passed!")
