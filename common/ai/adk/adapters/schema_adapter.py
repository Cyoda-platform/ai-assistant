"""
Schema adapter implementation for Google ADK Agent.

Provides concrete implementation for handling JSON schema operations,
including sanitization for Google ADK compatibility and response format creation.
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


class AdkSchemaAdapter(SchemaAdapterInterface):
    """
    Concrete implementation of JSON schema adaptation and validation for Google ADK.
    
    Handles schema sanitization for Google ADK compatibility, response format
    creation, and schema validation operations.
    """

    def sanitize_schema_for_agent(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize JSON schema to be compatible with Google ADK.
        
        Google ADK may have different restrictions compared to OpenAI.
        This method removes unsupported features and ensures compatibility.
        
        Args:
            schema: Original JSON schema
            
        Returns:
            Sanitized schema compatible with Google ADK
        """
        def clean_schema_recursive(obj):
            if isinstance(obj, dict):
                cleaned = {}
                for key, value in obj.items():
                    # Google ADK may be more permissive than OpenAI
                    # Remove known problematic features
                    if key in ['if', 'then', 'else']:
                        logger.debug(f"Removing unsupported ADK schema feature: {key}")
                        continue

                    # Handle specific Google ADK requirements
                    if key == 'type' and isinstance(value, list):
                        # Convert type arrays to single type (take first valid type)
                        cleaned[key] = value[0] if value else 'string'
                    else:
                        cleaned[key] = clean_schema_recursive(value)
                return cleaned
            elif isinstance(obj, list):
                return [clean_schema_recursive(item) for item in obj]
            else:
                return obj

        sanitized = clean_schema_recursive(schema)

        # Ensure required top-level properties for Google ADK compatibility
        if 'type' not in sanitized:
            sanitized['type'] = 'object'

        logger.debug("Sanitized schema for Google ADK")
        return sanitized

    def create_response_format(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create proper response_format structure for Google ADK structured outputs.
        
        Google ADK may use a different format than OpenAI for structured outputs.
        
        Args:
            schema: JSON schema for the expected response structure
            
        Returns:
            Properly formatted response_format dictionary for Google ADK
        """
        try:
            # Sanitize schema for Google ADK compatibility
            sanitized_schema = self.sanitize_schema_for_agent(schema)

            # Extract or generate schema name
            schema_name = self.generate_schema_name(sanitized_schema)

            # Google ADK response format (may be different from OpenAI)
            # This is a placeholder - actual format depends on ADK documentation
            response_format = {
                "type": "json_schema",
                "schema": sanitized_schema,
                "name": schema_name
            }

            logger.debug(f"Created Google ADK response_format with schema name: {schema_name}")
            return response_format

        except Exception as e:
            logger.warning(f"Failed to create Google ADK response_format: {e}")
            # Fallback to simple JSON object mode
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
        Generate a valid schema name for Google ADK response format.
        
        Args:
            schema: JSON schema
            
        Returns:
            Valid schema name for Google ADK
        """
        # Extract or generate schema name
        schema_name = schema.get('title', 'adk_response_schema')
        
        # Ensure name is valid (alphanumeric and underscores only)
        schema_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in schema_name)
        
        # Ensure it doesn't start with a number
        if schema_name and schema_name[0].isdigit():
            schema_name = f"adk_schema_{schema_name}"
            
        # Ensure it's not empty
        if not schema_name:
            schema_name = "adk_response_schema"
            
        return schema_name

    def is_schema_compatible(self, schema: Dict[str, Any]) -> bool:
        """
        Check if a schema is compatible with Google ADK.
        
        Args:
            schema: JSON schema to check
            
        Returns:
            True if compatible, False otherwise
        """
        # Google ADK may be more permissive than OpenAI
        # Check for known problematic features
        problematic_features = ['if', 'then', 'else']
        
        def check_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in problematic_features:
                        return False
                    if not check_recursive(value):
                        return False
            elif isinstance(obj, list):
                for item in obj:
                    if not check_recursive(item):
                        return False
            return True
        
        return check_recursive(schema)
