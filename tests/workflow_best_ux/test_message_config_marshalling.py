"""
Test Message Configuration Marshalling

Tests that message.py files can be marshalled into their config JSON automatically.
"""

import pytest
import json
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from workflow_best_ux.messages.welcome_message.message import WelcomeMessage


class TestMessageConfigMarshalling:
    """Test message configuration marshalling to JSON"""
    
    def test_message_has_get_config_method(self):
        """Test that message has get_config method"""
        message = WelcomeMessage()
        assert hasattr(message, 'get_config'), "Message must have get_config method"
        assert callable(message.get_config), "get_config must be callable"
    
    def test_message_get_config_returns_message_config(self):
        """Test that get_config returns MessageConfig interface"""
        message = WelcomeMessage()
        config = message.get_config()
        
        # Check that it implements MessageConfig interface
        assert hasattr(config, 'get_name'), "Config must have get_name method"
        assert hasattr(config, 'get_content'), "Config must have get_content method"
        assert callable(config.get_name), "get_name must be callable"
        assert callable(config.get_content), "get_content must be callable"
    
    def test_message_config_has_required_properties(self):
        """Test that message config has all required properties for JSON marshalling"""
        message = WelcomeMessage()
        config = message.get_config()
        
        # Check required properties exist
        assert hasattr(config, 'message_type'), "Config must have message_type"
        
        # Check properties have correct types
        assert isinstance(config.message_type, str), "Message type must be string"
        
        # Check content
        content = config.get_content()
        assert isinstance(content, str), "Content must be string"
    
    def test_message_config_can_be_marshalled_to_dict(self):
        """Test that message config can be converted to dictionary"""
        message = WelcomeMessage()
        config = message.get_config()
        
        # Create dictionary representation
        config_dict = {
            "name": WelcomeMessage.get_name(),
            "content": config.get_content(),
            "message_type": config.message_type
        }
        
        # Verify dictionary structure
        assert isinstance(config_dict, dict), "Config must be convertible to dict"
        assert "name" in config_dict, "Config dict must have name"
        assert "content" in config_dict, "Config dict must have content"
        assert "message_type" in config_dict, "Config dict must have message_type"
        
        # Verify values
        assert config_dict["name"] == "welcome_message", "Name must match get_name()"
        assert isinstance(config_dict["content"], str), "Content must be string"
        assert isinstance(config_dict["message_type"], str), "Message type must be string"
    
    def test_message_config_can_be_marshalled_to_json(self):
        """Test that message config can be converted to JSON"""
        message = WelcomeMessage()
        config = message.get_config()
        
        # Create JSON representation
        config_dict = {
            "name": WelcomeMessage.get_name(),
            "content": config.get_content(),
            "message_type": config.message_type
        }
        
        # Convert to JSON
        json_str = json.dumps(config_dict, indent=2)
        
        # Verify JSON is valid
        assert isinstance(json_str, str), "JSON must be string"
        
        # Parse back to verify structure
        parsed = json.loads(json_str)
        assert parsed == config_dict, "JSON round-trip must preserve data"
    
    def test_message_static_get_name_method(self):
        """Test that message has static get_name method"""
        # Test static method exists
        assert hasattr(WelcomeMessage, 'get_name'), "Message must have static get_name method"
        assert callable(WelcomeMessage.get_name), "get_name must be callable"
        
        # Test static method returns correct name
        name = WelcomeMessage.get_name()
        assert isinstance(name, str), "get_name must return string"
        assert name == "welcome_message", "get_name must return correct name"
    
    def test_message_content_loading(self):
        """Test that message can load content from markdown file"""
        message = WelcomeMessage()
        content = message.read_content()
        
        # Content should be loaded (either from file or default)
        assert isinstance(content, str), "Content must be string"
        assert len(content) > 0, "Content must not be empty"
    
    def test_message_config_marshalling_integration(self):
        """Integration test for complete message config marshalling"""
        message = WelcomeMessage()
        
        # Get configuration
        config = message.get_config()
        
        # Create complete JSON representation
        message_json = {
            "type": "message",
            "name": message.get_name(),
            "config": {
                "content": config.get_content(),
                "message_type": config.message_type
            }
        }
        
        # Convert to JSON and verify
        json_str = json.dumps(message_json, indent=2)
        parsed = json.loads(json_str)
        
        # Verify structure
        assert parsed["type"] == "message"
        assert parsed["name"] == "welcome_message"
        assert "config" in parsed
        assert "content" in parsed["config"]
        assert "message_type" in parsed["config"]
        
        print("✅ Message config marshalling test passed!")
        print(f"Generated JSON:\n{json_str}")
    
    def test_message_processor_interface(self):
        """Test that message implements MessageProcessor interface"""
        message = WelcomeMessage()
        
        # Check MessageProcessor interface
        assert hasattr(message, 'process'), "Message must have process method"
        assert callable(message.process), "process must be callable"
        
        # Check get_config method
        assert hasattr(message, 'get_config'), "Message must have get_config method"
        assert callable(message.get_config), "get_config must be callable"
    
    def test_message_process_method(self):
        """Test that message process method works"""
        import asyncio
        
        async def test_process():
            message = WelcomeMessage()
            context = {
                "user_name": "TestUser",
                "platform_name": "TestPlatform"
            }
            
            result = await message.process(context)
            
            # Check result structure
            assert isinstance(result, dict), "Process result must be dict"
            assert "message" in result, "Result must have message"
            assert "message_type" in result, "Result must have message_type"
            assert "status" in result, "Result must have status"
            
            # Check values
            assert isinstance(result["message"], str), "Message must be string"
            assert result["message_type"] == "welcome", "Message type must be welcome"
            assert result["status"] == "completed", "Status must be completed"
        
        # Run async test
        asyncio.run(test_process())


if __name__ == "__main__":
    test = TestMessageConfigMarshalling()
    test.test_message_has_get_config_method()
    test.test_message_get_config_returns_message_config()
    test.test_message_config_has_required_properties()
    test.test_message_config_can_be_marshalled_to_dict()
    test.test_message_config_can_be_marshalled_to_json()
    test.test_message_static_get_name_method()
    test.test_message_content_loading()
    test.test_message_config_marshalling_integration()
    test.test_message_processor_interface()
    test.test_message_process_method()
    print("🎉 All message config marshalling tests passed!")
