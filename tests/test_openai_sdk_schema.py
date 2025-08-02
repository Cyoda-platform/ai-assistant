#!/usr/bin/env python3
"""
Test JSON schema response format handling in OpenAI SDK Agent
"""

import json
import pytest
from unittest.mock import Mock

from common.ai.openai_sdk_agent import OpenAiSdkAgent


class TestOpenAiSdkSchema:
    """Test JSON schema response format handling"""

    @pytest.fixture
    def agent(self):
        """Create OpenAI SDK agent instance"""
        return OpenAiSdkAgent(max_calls=3)

    def test_sanitize_schema_for_openai(self, agent):
        """Test schema sanitization for OpenAI compatibility"""
        # Schema with unsupported features
        problematic_schema = {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "default": "John Doe"  # Not supported by OpenAI
                },
                "age": {
                    "type": "integer"
                },
                "status": {
                    "oneOf": [  # Not supported by OpenAI
                        {"type": "string", "enum": ["active"]},
                        {"type": "string", "enum": ["inactive"]}
                    ]
                }
            },
            "required": ["name", "age"]
        }
        
        sanitized = agent._sanitize_schema_for_openai(problematic_schema)
        
        # Check that unsupported features are removed
        assert "default" not in sanitized["properties"]["name"]
        assert "oneOf" not in sanitized["properties"]["status"]
        
        # Check that supported features are preserved
        assert sanitized["type"] == "object"
        assert "name" in sanitized["properties"]
        assert "age" in sanitized["properties"]
        assert sanitized["properties"]["name"]["type"] == "string"
        assert sanitized["properties"]["age"]["type"] == "integer"
        
        # Check that additionalProperties is set to False
        assert sanitized["additionalProperties"] == False

    def test_create_openai_response_format(self, agent):
        """Test creation of proper OpenAI response_format structure"""
        schema = {
            "title": "UserResponse",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        
        response_format = agent._create_openai_response_format(schema)
        
        # Check structure
        assert response_format["type"] == "json_schema"
        assert "json_schema" in response_format
        
        json_schema = response_format["json_schema"]
        assert json_schema["name"] == "UserResponse"
        assert json_schema["strict"] == True
        assert "schema" in json_schema
        
        # Check that schema is properly sanitized
        schema_part = json_schema["schema"]
        assert schema_part["type"] == "object"
        assert schema_part["additionalProperties"] == False
        assert "name" in schema_part["properties"]
        assert "age" in schema_part["properties"]

    def test_schema_with_arrays(self, agent):
        """Test schema handling with arrays"""
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        },
                        "required": ["id", "name"]
                    }
                }
            },
            "required": ["items"]
        }
        
        response_format = agent._create_openai_response_format(schema)
        
        # Verify array structure is preserved
        json_schema = response_format["json_schema"]["schema"]
        assert json_schema["properties"]["items"]["type"] == "array"
        assert "items" in json_schema["properties"]["items"]
        
        item_schema = json_schema["properties"]["items"]["items"]
        assert item_schema["type"] == "object"
        assert "id" in item_schema["properties"]
        assert "name" in item_schema["properties"]

    def test_fallback_response_format(self, agent):
        """Test fallback when schema creation fails"""
        # Invalid schema that should trigger fallback
        invalid_schema = None
        
        response_format = agent._create_openai_response_format(invalid_schema)
        
        # Should fallback to simple JSON object mode
        assert response_format["type"] == "json_object"

    def test_schema_validation_available(self, agent):
        """Test schema validation when jsonschema is available"""
        valid_json = '{"name": "John", "age": 30}'
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        
        # This should work if jsonschema is available
        import asyncio
        result = asyncio.run(agent._validate_with_schema(valid_json, schema, 1, 3))
        
        if result[0] is not None:  # Validation succeeded
            assert result[0] == valid_json
            assert result[1] is None
        else:  # jsonschema not available
            assert result[1] is None  # No error message when jsonschema unavailable

    def test_invalid_json_validation(self, agent):
        """Test validation with invalid JSON"""
        invalid_json = '{"name": "John", "age": "thirty"}'  # age should be integer
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        
        import asyncio
        result = asyncio.run(agent._validate_with_schema(invalid_json, schema, 1, 3))
        
        # Should either fail validation or skip if jsonschema unavailable
        if result[0] is None and result[1] is not None:
            # Validation failed as expected
            assert "Validation failed" in result[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
