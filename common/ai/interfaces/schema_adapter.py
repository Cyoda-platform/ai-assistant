"""
Schema adapter interface for AI Agents.

Defines the contract for handling JSON schema operations, including
sanitization for different AI agent SDK compatibility and response format creation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple


class SchemaAdapterInterface(ABC):
    """
    Abstract interface for JSON schema adaptation and validation.
    
    Handles schema sanitization for AI agent SDK compatibility, response format
    creation, and schema validation operations.
    """

    @abstractmethod
    def sanitize_schema_for_agent(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize JSON schema to be compatible with the specific AI agent SDK.
        
        Args:
            schema: Original JSON schema
            
        Returns:
            Sanitized schema compatible with the agent SDK
        """
        pass

    @abstractmethod
    def create_response_format(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create proper response_format structure for structured outputs.
        
        Args:
            schema: JSON schema for the expected response structure
            
        Returns:
            Properly formatted response_format dictionary for the agent SDK
        """
        pass

    @abstractmethod
    def validate_schema(self, data: str, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate data against JSON schema.
        
        Args:
            data: JSON string to validate
            schema: JSON schema for validation
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @abstractmethod
    def generate_schema_name(self, schema: Dict[str, Any]) -> str:
        """
        Generate a valid schema name for the agent SDK response format.
        
        Args:
            schema: JSON schema
            
        Returns:
            Valid schema name for the specific agent SDK
        """
        pass

    @abstractmethod
    def is_schema_compatible(self, schema: Dict[str, Any]) -> bool:
        """
        Check if a schema is compatible with the agent SDK.
        
        Args:
            schema: JSON schema to check
            
        Returns:
            True if compatible, False otherwise
        """
        pass
