"""
Message adapter implementation for Google ADK Agent.

Provides concrete implementation for converting between AIMessage objects
and the standard message format expected by the Google ADK.
"""

import logging
from typing import List, Dict, Any

from entity.model import AIMessage
from common.ai.interfaces.message_adapter import MessageAdapterInterface

logger = logging.getLogger(__name__)


class AdkMessageAdapter(MessageAdapterInterface):
    """
    Concrete implementation of message format adaptation for Google ADK.
    
    Converts AIMessage objects to the standard message format used by
    the Google ADK, with proper validation and error handling.
    """

    def adapt_messages(self, messages: List[AIMessage]) -> List[Dict[str, str]]:
        """
        Convert AIMessage objects to standard message format for Google ADK.
        
        Args:
            messages: List of AIMessage objects to convert
            
        Returns:
            List of dictionaries with 'role' and 'content' keys
        """
        adapted_messages = []
        
        for message in messages:
            if not isinstance(message, AIMessage) or not message.content:
                logger.warning(f"Skipping invalid message: {message}")
                continue
                
            # Convert content to string
            content = self._convert_content_to_string(message.content)
            
            # Google ADK uses similar role structure to OpenAI
            adapted_message = {
                "role": self._normalize_role(message.role),
                "content": content
            }
            
            if self.validate_message_format(adapted_message):
                adapted_messages.append(adapted_message)
            else:
                logger.warning(f"Invalid message format after adaptation: {adapted_message}")
        
        logger.debug(f"Adapted {len(adapted_messages)} messages from {len(messages)} input messages")
        return adapted_messages

    def validate_message_format(self, message: Dict[str, str]) -> bool:
        """
        Validate that a message has the correct format for Google ADK.
        
        Args:
            message: Message dictionary to validate
            
        Returns:
            True if message format is valid, False otherwise
        """
        if not isinstance(message, dict):
            return False
            
        required_keys = {'role', 'content'}
        if not required_keys.issubset(message.keys()):
            return False
            
        if not isinstance(message['role'], str) or not isinstance(message['content'], str):
            return False
            
        # Google ADK supports similar roles to OpenAI
        valid_roles = {'user', 'assistant', 'system', 'model'}
        if message['role'] not in valid_roles:
            logger.warning(f"Unknown role: {message['role']}, but allowing it")
            
        return True

    def create_default_message(self) -> Dict[str, str]:
        """
        Create a default message when no messages are provided.
        
        Returns:
            Default message dictionary for Google ADK
        """
        return {
            "role": "user",
            "content": "Please help me."
        }

    def _convert_content_to_string(self, content: Any) -> str:
        """
        Convert message content to string format.
        
        Args:
            content: Message content (can be string, list, or other types)
            
        Returns:
            String representation of the content
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # Join list items with space
            return " ".join(str(item) for item in content)
        else:
            # Convert other types to string
            return str(content)

    def _normalize_role(self, role: str) -> str:
        """
        Normalize role names for Google ADK compatibility.
        
        Args:
            role: Original role name
            
        Returns:
            Normalized role name
        """
        if not role:
            return 'user'
            
        # Google ADK uses 'model' instead of 'assistant' in some contexts
        role_mapping = {
            'assistant': 'assistant',  # Keep as assistant for consistency
            'user': 'user',
            'system': 'system',
            'model': 'model'
        }
        
        return role_mapping.get(role.lower(), 'user')
