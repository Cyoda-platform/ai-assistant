"""
Test Tool Configuration Marshalling

Tests that tool.py files can be marshalled into their config JSON automatically.
"""

import pytest
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from workflow_best_ux.tools.web_search.tool import WebSearchTool
from workflow_best_ux.tools.read_link.tool import ReadLinkTool
from workflow_best_ux.tools.get_cyoda_guidelines.tool import GetCyodaGuidelinesTool
from workflow_best_ux.tools.get_user_info.tool import GetUserInfoTool


class TestToolConfigMarshalling:
    """Test tool configuration marshalling to JSON"""
    
    @pytest.mark.parametrize("tool_class,expected_name", [
        (WebSearchTool, "web_search"),
        (ReadLinkTool, "read_link"),
        (GetCyodaGuidelinesTool, "get_cyoda_guidelines"),
        (GetUserInfoTool, "get_user_info")
    ])
    def test_tool_has_get_config_method(self, tool_class, expected_name):
        """Test that tool has get_config method"""
        tool = tool_class()
        assert hasattr(tool, 'get_config'), f"{tool_class.__name__} must have get_config method"
        assert callable(tool.get_config), f"{tool_class.__name__} get_config must be callable"
    
    @pytest.mark.parametrize("tool_class,expected_name", [
        (WebSearchTool, "web_search"),
        (ReadLinkTool, "read_link"),
        (GetCyodaGuidelinesTool, "get_cyoda_guidelines"),
        (GetUserInfoTool, "get_user_info")
    ])
    def test_tool_get_config_returns_tool_config(self, tool_class, expected_name):
        """Test that get_config returns ToolConfig interface"""
        tool = tool_class()
        config = tool.get_config()
        
        # Check that it implements ToolConfig interface
        assert hasattr(config, 'get_name'), f"{tool_class.__name__} config must have get_name method"
        assert hasattr(config, 'get_parameters'), f"{tool_class.__name__} config must have get_parameters method"
        assert callable(config.get_name), f"{tool_class.__name__} get_name must be callable"
        assert callable(config.get_parameters), f"{tool_class.__name__} get_parameters must be callable"
    
    @pytest.mark.parametrize("tool_class,expected_name", [
        (WebSearchTool, "web_search"),
        (ReadLinkTool, "read_link"),
        (GetCyodaGuidelinesTool, "get_cyoda_guidelines"),
        (GetUserInfoTool, "get_user_info")
    ])
    def test_tool_config_has_required_properties(self, tool_class, expected_name):
        """Test that tool config has all required properties for JSON marshalling"""
        tool = tool_class()
        config = tool.get_config()
        
        # Check required properties exist
        assert hasattr(config, 'description'), f"{tool_class.__name__} config must have description"
        
        # Check properties have correct types
        assert isinstance(config.description, str), f"{tool_class.__name__} description must be string"
        
        # Check parameters
        parameters = config.get_parameters()
        assert isinstance(parameters, dict), f"{tool_class.__name__} parameters must be dict"
    
    @pytest.mark.parametrize("tool_class,expected_name", [
        (WebSearchTool, "web_search"),
        (ReadLinkTool, "read_link"),
        (GetCyodaGuidelinesTool, "get_cyoda_guidelines"),
        (GetUserInfoTool, "get_user_info")
    ])
    def test_tool_config_can_be_marshalled_to_dict(self, tool_class, expected_name):
        """Test that tool config can be converted to dictionary"""
        tool = tool_class()
        config = tool.get_config()
        
        # Create dictionary representation
        config_dict = {
            "name": tool_class.get_name(),
            "description": config.description,
            "parameters": config.get_parameters()
        }
        
        # Verify dictionary structure
        assert isinstance(config_dict, dict), f"{tool_class.__name__} config must be convertible to dict"
        assert "name" in config_dict, f"{tool_class.__name__} config dict must have name"
        assert "description" in config_dict, f"{tool_class.__name__} config dict must have description"
        assert "parameters" in config_dict, f"{tool_class.__name__} config dict must have parameters"
        
        # Verify values
        assert config_dict["name"] == expected_name, f"{tool_class.__name__} name must match expected"
        assert isinstance(config_dict["description"], str), f"{tool_class.__name__} description must be string"
        assert isinstance(config_dict["parameters"], dict), f"{tool_class.__name__} parameters must be dict"
    
    @pytest.mark.parametrize("tool_class,expected_name", [
        (WebSearchTool, "web_search"),
        (ReadLinkTool, "read_link"),
        (GetCyodaGuidelinesTool, "get_cyoda_guidelines"),
        (GetUserInfoTool, "get_user_info")
    ])
    def test_tool_config_can_be_marshalled_to_json(self, tool_class, expected_name):
        """Test that tool config can be converted to JSON"""
        tool = tool_class()
        config = tool.get_config()
        
        # Create JSON representation
        config_dict = {
            "name": tool_class.get_name(),
            "description": config.description,
            "parameters": config.get_parameters()
        }
        
        # Convert to JSON
        json_str = json.dumps(config_dict, indent=2)
        
        # Verify JSON is valid
        assert isinstance(json_str, str), f"{tool_class.__name__} JSON must be string"
        
        # Parse back to verify structure
        parsed = json.loads(json_str)
        assert parsed == config_dict, f"{tool_class.__name__} JSON round-trip must preserve data"
    
    @pytest.mark.parametrize("tool_class,expected_name", [
        (WebSearchTool, "web_search"),
        (ReadLinkTool, "read_link"),
        (GetCyodaGuidelinesTool, "get_cyoda_guidelines"),
        (GetUserInfoTool, "get_user_info")
    ])
    def test_tool_static_get_name_method(self, tool_class, expected_name):
        """Test that tool has static get_name method"""
        # Test static method exists
        assert hasattr(tool_class, 'get_name'), f"{tool_class.__name__} must have static get_name method"
        assert callable(tool_class.get_name), f"{tool_class.__name__} get_name must be callable"
        
        # Test static method returns correct name
        name = tool_class.get_name()
        assert isinstance(name, str), f"{tool_class.__name__} get_name must return string"
        assert name == expected_name, f"{tool_class.__name__} get_name must return correct name"
    
    def test_web_search_tool_specific_parameters(self):
        """Test WebSearchTool specific parameter requirements"""
        tool = WebSearchTool()
        config = tool.get_config()
        parameters = config.get_parameters()
        
        # Check that query parameter exists and is required
        assert "query" in parameters, "WebSearchTool must have query parameter"
        query_param = parameters["query"]
        assert query_param["type"] == "string", "Query parameter must be string type"
        assert query_param["required"] == True, "Query parameter must be required"
    
    def test_read_link_tool_specific_parameters(self):
        """Test ReadLinkTool specific parameter requirements"""
        tool = ReadLinkTool()
        config = tool.get_config()
        parameters = config.get_parameters()
        
        # Check that url parameter exists and is required
        assert "url" in parameters, "ReadLinkTool must have url parameter"
        url_param = parameters["url"]
        assert url_param["type"] == "string", "URL parameter must be string type"
        assert url_param["required"] == True, "URL parameter must be required"
    
    def test_tool_config_marshalling_integration(self):
        """Integration test for complete tool config marshalling"""
        tool = WebSearchTool()
        
        # Get configuration
        config = tool.get_config()
        
        # Create complete JSON representation
        tool_json = {
            "type": "tool",
            "name": tool.get_name(),
            "config": {
                "description": config.description,
                "parameters": config.get_parameters()
            }
        }
        
        # Convert to JSON and verify
        json_str = json.dumps(tool_json, indent=2)
        parsed = json.loads(json_str)
        
        # Verify structure
        assert parsed["type"] == "tool"
        assert parsed["name"] == "web_search"
        assert "config" in parsed
        assert "description" in parsed["config"]
        assert "parameters" in parsed["config"]
        
        print("✅ Tool config marshalling test passed!")
        print(f"Generated JSON:\n{json_str}")


if __name__ == "__main__":
    test = TestToolConfigMarshalling()
    
    # Test all tools
    tools = [
        (WebSearchTool, "web_search"),
        (ReadLinkTool, "read_link"),
        (GetCyodaGuidelinesTool, "get_cyoda_guidelines"),
        (GetUserInfoTool, "get_user_info")
    ]
    
    for tool_class, expected_name in tools:
        test.test_tool_has_get_config_method(tool_class, expected_name)
        test.test_tool_get_config_returns_tool_config(tool_class, expected_name)
        test.test_tool_config_has_required_properties(tool_class, expected_name)
        test.test_tool_config_can_be_marshalled_to_dict(tool_class, expected_name)
        test.test_tool_config_can_be_marshalled_to_json(tool_class, expected_name)
        test.test_tool_static_get_name_method(tool_class, expected_name)
    
    test.test_web_search_tool_specific_parameters()
    test.test_read_link_tool_specific_parameters()
    test.test_tool_config_marshalling_integration()
    
    print("🎉 All tool config marshalling tests passed!")
