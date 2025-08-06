"""
Test Agent Configuration Marshalling

Tests that agent.py can be marshalled into its config JSON automatically.
"""

import pytest
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from workflow_best_ux.agents.chat_assistant.agent import ChatAssistantAgent


class TestAgentConfigMarshalling:
    """Test agent configuration marshalling to JSON"""
    
    def test_agent_has_get_config_method(self):
        """Test that agent has get_config method"""
        agent = ChatAssistantAgent()
        assert hasattr(agent, 'get_config'), "Agent must have get_config method"
        assert callable(agent.get_config), "get_config must be callable"
    
    def test_agent_get_config_returns_agent_config(self):
        """Test that get_config returns AgentConfig interface"""
        agent = ChatAssistantAgent()
        config = agent.get_config()
        
        # Check that it implements AgentConfig interface
        assert hasattr(config, 'get_name'), "Config must have get_name method"
        assert hasattr(config, 'get_tools'), "Config must have get_tools method"
        assert hasattr(config, 'get_prompts'), "Config must have get_prompts method"
        assert callable(config.get_name), "get_name must be callable"
        assert callable(config.get_tools), "get_tools must be callable"
        assert callable(config.get_prompts), "get_prompts must be callable"
    
    def test_agent_config_has_required_properties(self):
        """Test that agent config has all required properties for JSON marshalling"""
        agent = ChatAssistantAgent()
        config = agent.get_config()
        
        # Check required properties exist
        assert hasattr(config, 'description'), "Config must have description"
        assert hasattr(config, 'model_name'), "Config must have model_name"
        assert hasattr(config, 'temperature'), "Config must have temperature"
        assert hasattr(config, 'max_tokens'), "Config must have max_tokens"
        
        # Check properties have correct types
        assert isinstance(config.description, str), "Description must be string"
        assert isinstance(config.model_name, str), "Model name must be string"
        assert isinstance(config.temperature, (int, float)), "Temperature must be numeric"
        assert isinstance(config.max_tokens, int), "Max tokens must be integer"
    
    def test_agent_config_can_be_marshalled_to_dict(self):
        """Test that agent config can be converted to dictionary"""
        agent = ChatAssistantAgent()
        config = agent.get_config()
        
        # Create dictionary representation
        config_dict = {
            "name": ChatAssistantAgent.get_name(),
            "description": config.description,
            "model": {
                "model_name": config.model_name,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens
            },
            "tools": [tool.get_name() for tool in config.get_tools()],
            "prompts": [prompt.get_name() for prompt in config.get_prompts()]
        }
        
        # Verify dictionary structure
        assert isinstance(config_dict, dict), "Config must be convertible to dict"
        assert "name" in config_dict, "Config dict must have name"
        assert "description" in config_dict, "Config dict must have description"
        assert "model" in config_dict, "Config dict must have model"
        assert "tools" in config_dict, "Config dict must have tools"
        assert "prompts" in config_dict, "Config dict must have prompts"
        
        # Verify values
        assert config_dict["name"] == "chat_assistant", "Name must match get_name()"
        assert isinstance(config_dict["description"], str), "Description must be string"
        assert isinstance(config_dict["model"], dict), "Model must be dict"
        assert isinstance(config_dict["tools"], list), "Tools must be list"
        assert isinstance(config_dict["prompts"], list), "Prompts must be list"
    
    def test_agent_config_can_be_marshalled_to_json(self):
        """Test that agent config can be converted to JSON"""
        agent = ChatAssistantAgent()
        config = agent.get_config()
        
        # Create JSON representation
        config_dict = {
            "name": ChatAssistantAgent.get_name(),
            "description": config.description,
            "model": {
                "model_name": config.model_name,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens
            },
            "tools": [tool.get_name() for tool in config.get_tools()],
            "prompts": [prompt.get_name() for prompt in config.get_prompts()]
        }
        
        # Convert to JSON
        json_str = json.dumps(config_dict, indent=2)
        
        # Verify JSON is valid
        assert isinstance(json_str, str), "JSON must be string"
        
        # Parse back to verify structure
        parsed = json.loads(json_str)
        assert parsed == config_dict, "JSON round-trip must preserve data"
    
    def test_agent_static_get_name_method(self):
        """Test that agent has static get_name method"""
        # Test static method exists
        assert hasattr(ChatAssistantAgent, 'get_name'), "Agent must have static get_name method"
        assert callable(ChatAssistantAgent.get_name), "get_name must be callable"
        
        # Test static method returns correct name
        name = ChatAssistantAgent.get_name()
        assert isinstance(name, str), "get_name must return string"
        assert name == "chat_assistant", "get_name must return correct name"
        
        # Test static method can be called without instance
        assert ChatAssistantAgent.get_name() == "chat_assistant"
    
    def test_agent_config_marshalling_integration(self):
        """Integration test for complete agent config marshalling"""
        agent = ChatAssistantAgent()
        
        # Get configuration
        config = agent.get_config()
        
        # Create complete JSON representation
        agent_json = {
            "type": "agent",
            "name": agent.get_name(),
            "config": {
                "description": config.description,
                "model": {
                    "model_name": config.model_name,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens
                },
                "tools": [
                    {
                        "name": tool.get_name(),
                        "type": "tool"
                    } for tool in config.get_tools()
                ],
                "prompts": [
                    {
                        "name": prompt.get_name(),
                        "type": "prompt"
                    } for prompt in config.get_prompts()
                ]
            }
        }
        
        # Convert to JSON and verify
        json_str = json.dumps(agent_json, indent=2)
        parsed = json.loads(json_str)
        
        # Verify structure
        assert parsed["type"] == "agent"
        assert parsed["name"] == "chat_assistant"
        assert "config" in parsed
        assert "description" in parsed["config"]
        assert "model" in parsed["config"]
        assert "tools" in parsed["config"]
        assert "prompts" in parsed["config"]
        
        print("✅ Agent config marshalling test passed!")
        print(f"Generated JSON:\n{json_str}")


if __name__ == "__main__":
    test = TestAgentConfigMarshalling()
    test.test_agent_has_get_config_method()
    test.test_agent_get_config_returns_agent_config()
    test.test_agent_config_has_required_properties()
    test.test_agent_config_can_be_marshalled_to_dict()
    test.test_agent_config_can_be_marshalled_to_json()
    test.test_agent_static_get_name_method()
    test.test_agent_config_marshalling_integration()
    print("🎉 All agent config marshalling tests passed!")
