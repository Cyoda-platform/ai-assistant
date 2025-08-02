"""
Tests for the modular OpenAI SDK Agent implementation.

Tests the individual components and their integration to ensure
the refactored modular structure works correctly.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock

from common.ai.openai_sdk.context import OpenAiSdkAgentContext
from common.ai.openai_sdk.adapters.message_adapter import MessageAdapter
from common.ai.openai_sdk.adapters.ui_function_handler import UiFunctionHandler
from common.ai.openai_sdk.adapters.schema_adapter import SchemaAdapter
from entity.model import AIMessage


class TestOpenAiSdkAgentContext:
    """Test the agent context class."""

    def test_context_initialization(self):
        """Test context initialization with all parameters."""
        methods_dict = {"test_method": Mock()}
        technical_id = "test_123"
        cls_instance = Mock()
        entity = Mock()

        context = OpenAiSdkAgentContext(
            methods_dict=methods_dict,
            technical_id=technical_id,
            cls_instance=cls_instance,
            entity=entity
        )

        assert context.methods_dict == methods_dict
        assert context.technical_id == technical_id
        assert context.cls_instance == cls_instance
        assert context.entity == entity

    def test_has_method(self):
        """Test method existence checking."""
        methods_dict = {"existing_method": Mock()}
        context = OpenAiSdkAgentContext(methods_dict, "test", Mock(), Mock())

        assert context.has_method("existing_method") is True
        assert context.has_method("non_existing_method") is False

    def test_get_method(self):
        """Test method retrieval."""
        test_method = Mock()
        methods_dict = {"test_method": test_method}
        context = OpenAiSdkAgentContext(methods_dict, "test", Mock(), Mock())

        assert context.get_method("test_method") == test_method

        with pytest.raises(KeyError):
            context.get_method("non_existing_method")

    def test_get_context_params(self):
        """Test context parameter extraction."""
        technical_id = "test_123"
        entity = Mock()
        context = OpenAiSdkAgentContext({}, technical_id, Mock(), entity)

        params = context.get_context_params()
        assert params == {"technical_id": technical_id, "entity": entity}


class TestMessageAdapter:
    """Test the message adapter implementation."""

    def setup_method(self):
        """Setup for each test method."""
        self.adapter = MessageAdapter()

    def test_adapt_messages_basic(self):
        """Test basic message adaptation."""
        messages = [
            AIMessage(role="user", content="Hello"),
            AIMessage(role="assistant", content="Hi there")
        ]

        adapted = self.adapter.adapt_messages(messages)

        assert len(adapted) == 2
        assert adapted[0] == {"role": "user", "content": "Hello"}
        assert adapted[1] == {"role": "assistant", "content": "Hi there"}

    def test_adapt_messages_list_content(self):
        """Test message adaptation with list content."""
        messages = [
            AIMessage(role="user", content=["Hello", "world"])
        ]

        adapted = self.adapter.adapt_messages(messages)

        assert len(adapted) == 1
        assert adapted[0] == {"role": "user", "content": "Hello world"}

    def test_adapt_messages_invalid(self):
        """Test message adaptation with invalid messages."""
        messages = [
            AIMessage(role="user", content="Valid message"),
            AIMessage(role="user", content=None),  # Invalid
            None  # Invalid
        ]

        adapted = self.adapter.adapt_messages(messages)

        assert len(adapted) == 1
        assert adapted[0] == {"role": "user", "content": "Valid message"}

    def test_validate_message_format(self):
        """Test message format validation."""
        valid_message = {"role": "user", "content": "Hello"}
        invalid_message_1 = {"role": "user"}  # Missing content
        invalid_message_2 = {"content": "Hello"}  # Missing role
        invalid_message_3 = {"role": 123, "content": "Hello"}  # Invalid role type

        assert self.adapter.validate_message_format(valid_message) is True
        assert self.adapter.validate_message_format(invalid_message_1) is False
        assert self.adapter.validate_message_format(invalid_message_2) is False
        assert self.adapter.validate_message_format(invalid_message_3) is False

    def test_create_default_message(self):
        """Test default message creation."""
        default = self.adapter.create_default_message()
        assert default == {"role": "user", "content": "Please help me."}


class TestUiFunctionHandler:
    """Test the UI function handler implementation."""

    def setup_method(self):
        """Setup for each test method."""
        self.handler = UiFunctionHandler()

    def test_is_ui_function(self):
        """Test UI function detection."""
        assert self.handler.is_ui_function("ui_function_test") is True
        assert self.handler.is_ui_function("regular_function") is False

    def test_handle_ui_function(self):
        """Test UI function handling."""
        result = self.handler.handle_ui_function("ui_function_test", {"param": "value"})
        
        # Should return JSON with single quotes
        expected = "{'type': 'ui_function', 'function': 'ui_function_test', 'param': 'value'}"
        assert result == expected

    def test_extract_ui_function_names(self):
        """Test UI function name extraction from tools."""
        tools = [
            {
                "type": "function",
                "function": {"name": "ui_function_test1"}
            },
            {
                "type": "function", 
                "function": {"name": "regular_function"}
            },
            {
                "type": "function",
                "function": {"name": "ui_function_test2"}
            }
        ]

        ui_names = self.handler.extract_ui_function_names(tools)
        assert ui_names == ["ui_function_test1", "ui_function_test2"]

    def test_is_ui_function_json(self):
        """Test UI function JSON detection."""
        ui_json = '{"type": "ui_function", "function": "ui_function_test"}'
        regular_json = '{"type": "regular", "data": "value"}'
        invalid_json = "not json"

        assert self.handler.is_ui_function_json(ui_json) is True
        assert self.handler.is_ui_function_json(regular_json) is False
        assert self.handler.is_ui_function_json(invalid_json) is False

    def test_enhance_ui_function_description(self):
        """Test UI function description enhancement."""
        original = "Test function"
        enhanced = self.handler.enhance_ui_function_description(original)
        
        assert "CRITICAL" in enhanced
        assert "raw JSON output" in enhanced
        assert original in enhanced


class TestSchemaAdapter:
    """Test the schema adapter implementation."""

    def setup_method(self):
        """Setup for each test method."""
        self.adapter = SchemaAdapter()

    def test_sanitize_schema_for_agent(self):
        """Test schema sanitization for agent compatibility."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "default": "test"},
                "age": {"type": ["integer", "null"]},
                "data": {"oneOf": [{"type": "string"}, {"type": "number"}]}
            },
            "additionalProperties": True
        }

        sanitized = self.adapter.sanitize_schema_for_agent(schema)

        # Should remove unsupported features
        assert "default" not in str(sanitized)
        assert "oneOf" not in str(sanitized)
        assert sanitized["additionalProperties"] is False
        assert sanitized["properties"]["age"]["type"] == "integer"  # First type from array

    def test_generate_schema_name(self):
        """Test schema name generation."""
        schema_with_title = {"title": "TestSchema"}
        schema_without_title = {"type": "object"}
        schema_with_invalid_title = {"title": "Test-Schema!@#"}

        assert self.adapter.generate_schema_name(schema_with_title) == "TestSchema"
        assert self.adapter.generate_schema_name(schema_without_title) == "response_schema"
        assert self.adapter.generate_schema_name(schema_with_invalid_title) == "Test_Schema___"

    def test_create_response_format(self):
        """Test response format creation."""
        schema = {
            "type": "object",
            "title": "TestResponse",
            "properties": {"message": {"type": "string"}}
        }

        response_format = self.adapter.create_response_format(schema)

        assert response_format["type"] == "json_schema"
        assert "json_schema" in response_format
        assert response_format["json_schema"]["name"] == "TestResponse"
        assert response_format["json_schema"]["strict"] is True

    def test_is_schema_compatible(self):
        """Test schema compatibility checking."""
        compatible_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}}
        }

        incompatible_schema = {
            "type": "object",
            "properties": {"name": {"type": "string", "default": "test"}}
        }

        assert self.adapter.is_schema_compatible(compatible_schema) is True
        assert self.adapter.is_schema_compatible(incompatible_schema) is False


if __name__ == "__main__":
    pytest.main([__file__])
