"""
Schema adapter implementation for OpenAI SDK Agent.

Provides concrete implementation for handling JSON schema operations,
including sanitization for OpenAI compatibility and response format creation.
"""

import logging
from typing import Dict, Any, Optional, Tuple

try:
    import jsonschema
    from jsonschema import ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    jsonschema = None
    ValidationError = Exception
    JSONSCHEMA_AVAILABLE = False

from common.ai.interfaces.schema_adapter import SchemaAdapterInterface

logger = logging.getLogger(__name__)


class SchemaAdapter(SchemaAdapterInterface):
    """
    Concrete implementation of JSON schema adaptation and validation.
    
    Handles schema sanitization for OpenAI compatibility, response format
    creation, and schema validation operations.
    """

    def sanitize_schema_for_agent(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize JSON schema to be compatible with OpenAI's structured outputs.
        
        OpenAI has specific restrictions on JSON schema features for structured outputs.
        This method removes unsupported features and ensures compatibility.
        
        Unsupported features that are removed:
        - default values
        - oneOf, anyOf, allOf, not conditionals
        - if/then/else conditionals
        - type arrays (converted to single type)
        
        Args:
            schema: Original JSON schema
            
        Returns:
            Sanitized schema compatible with OpenAI structured outputs
        """
        def clean_schema_recursive(obj):
            if isinstance(obj, dict):
                cleaned = {}
                for key, value in obj.items():
                    # Remove unsupported schema features
                    if key in ['default', 'oneOf', 'anyOf', 'allOf', 'not', 'if', 'then', 'else']:
                        logger.debug(f"Removing unsupported schema feature: {key}")
                        continue

                    # Handle specific OpenAI requirements
                    if key == 'type' and isinstance(value, list):
                        # Convert type arrays to single type (take first valid type)
                        cleaned[key] = value[0] if value else 'string'
                    elif key == 'additionalProperties':
                        # OpenAI requires explicit false for additionalProperties in strict mode
                        cleaned[key] = False
                    else:
                        cleaned[key] = clean_schema_recursive(value)
                return cleaned
            elif isinstance(obj, list):
                return [clean_schema_recursive(item) for item in obj]
            else:
                return obj

        sanitized = clean_schema_recursive(schema)

        # Ensure required top-level properties for OpenAI compatibility
        if 'type' not in sanitized:
            sanitized['type'] = 'object'
        if 'additionalProperties' not in sanitized:
            sanitized['additionalProperties'] = False

        logger.debug("Sanitized schema for OpenAI: removed unsupported features")
        return sanitized

    def create_response_format(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create proper OpenAI response_format structure for structured outputs.
        
        OpenAI structured outputs require a specific format:
        {
            "type": "json_schema",
            "json_schema": {
                "name": "response_schema_name",
                "schema": {...},
                "strict": true
            }
        }
        
        Args:
            schema: JSON schema for the expected response structure
            
        Returns:
            Properly formatted OpenAI response_format dictionary
        """
        try:
            # Sanitize schema for OpenAI compatibility
            sanitized_schema = self.sanitize_schema_for_agent(schema)

            # Extract or generate schema name
            schema_name = self.generate_schema_name(sanitized_schema)

            # Create proper OpenAI response_format structure
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "schema": sanitized_schema,
                    "strict": True  # Enable strict mode for better validation
                }
            }

            logger.debug(f"Created OpenAI response_format with schema name: {schema_name}")
            return response_format

        except Exception as e:
            logger.warning(f"Failed to create OpenAI response_format: {e}")
            # Fallback to simple JSON object mode (less strict but more compatible)
            return {"type": "json_object"}

    def validate_schema(self, data: str, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate data against JSON schema.
        
        Args:
            data: JSON string to validate
            schema: JSON schema for validation
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.warning("jsonschema not available, skipping validation")
            return True, None

        try:
            import json
            parsed_data = json.loads(data)
            jsonschema.validate(instance=parsed_data, schema=schema)
            return True, None
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON: {str(e)}"
            return False, error_msg
        except ValidationError as e:
            error_msg = str(e)
            # Truncate long error messages
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + '...'
            return False, error_msg
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            return False, error_msg

    def generate_schema_name(self, schema: Dict[str, Any]) -> str:
        """
        Generate a valid schema name for OpenAI response format.
        
        Args:
            schema: JSON schema
            
        Returns:
            Valid schema name (alphanumeric and underscores only)
        """
        # Extract or generate schema name
        schema_name = schema.get('title', 'response_schema')
        
        # Ensure name is valid (alphanumeric and underscores only)
        schema_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in schema_name)
        
        # Ensure it doesn't start with a number
        if schema_name and schema_name[0].isdigit():
            schema_name = f"schema_{schema_name}"
            
        # Ensure it's not empty
        if not schema_name:
            schema_name = "response_schema"
            
        return schema_name

    def is_schema_compatible(self, schema: Dict[str, Any]) -> bool:
        """
        Check if a schema is compatible with OpenAI structured outputs.
        
        Args:
            schema: JSON schema to check
            
        Returns:
            True if compatible, False otherwise
        """
        # Check for unsupported features
        unsupported_features = ['default', 'oneOf', 'anyOf', 'allOf', 'not', 'if', 'then', 'else']
        
        def check_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in unsupported_features:
                        return False
                    if key == 'type' and isinstance(value, list):
                        return False  # Type arrays not supported
                    if not check_recursive(value):
                        return False
            elif isinstance(obj, list):
                for item in obj:
                    if not check_recursive(item):
                        return False
            return True
        
        return check_recursive(schema)
