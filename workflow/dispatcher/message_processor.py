import logging
from typing import List, Dict, Any, Optional

import common.config.const as const
from common.config.config import config as env_config
from common.utils.utils import get_current_timestamp_num
from entity.model import FlowEdgeMessage, AIMessage

logger = logging.getLogger(__name__)


class MessageProcessor:
    """
    Handles message processing, formatting, and flow management for workflow dispatcher.
    """
    
    def __init__(self, memory_manager):
        """
        Initialize the message processor.
        
        Args:
            memory_manager: Memory manager for message operations
        """
        self.memory_manager = memory_manager
    
    def format_ai_response(self, response: str, config: Dict[str, Any]) -> str:
        """
        Format AI response based on configuration.
        
        Args:
            response: Raw AI response
            config: Configuration for formatting
            
        Returns:
            Formatted response
        """
        try:
            # Apply any formatting rules from config
            format_config = config.get("format", {})
            
            # Handle different format types
            format_type = format_config.get("type", "plain")
            
            if format_type == "json":
                return self._format_as_json(response, format_config)
            elif format_type == "markdown":
                return self._format_as_markdown(response, format_config)
            elif format_type == "code":
                return self._format_as_code(response, format_config)
            else:
                return response  # Return as-is for plain format
                
        except Exception as e:
            logger.warning(f"Error formatting response: {e}")
            return response  # Return original if formatting fails
    
    def _format_as_json(self, response: str, format_config: Dict[str, Any]) -> str:
        """Format response as JSON."""
        try:
            import json
            # Try to parse and reformat if it's already JSON
            parsed = json.loads(response)
            indent = format_config.get("indent", 2)
            return json.dumps(parsed, indent=indent)
        except json.JSONDecodeError:
            # If not JSON, wrap in a JSON structure
            return json.dumps({"response": response}, indent=format_config.get("indent", 2))
    
    def _format_as_markdown(self, response: str, format_config: Dict[str, Any]) -> str:
        """Format response as Markdown."""
        title = format_config.get("title", "AI Response")
        return f"# {title}\n\n{response}"
    
    def _format_as_code(self, response: str, format_config: Dict[str, Any]) -> str:
        """Format response as code block."""
        language = format_config.get("language", "")
        return f"```{language}\n{response}\n```"
    
    async def process_flow_messages(self, flow: List[FlowEdgeMessage], entity, 
                                   user_id: str, content: str) -> FlowEdgeMessage:
        """
        Process and add a message to the flow.
        
        Args:
            flow: List of flow edge messages
            entity: Entity context
            user_id: User ID
            content: Message content
            
        Returns:
            Created FlowEdgeMessage
        """
        try:
            message = FlowEdgeMessage(
                type="ai_response",
                publish=True,
                last_modified=get_current_timestamp_num(),
                user_id=user_id
            )
            
            return await self.memory_manager.add_edge_message(message, flow, user_id)
            
        except Exception as e:
            logger.error(f"Error processing flow message: {e}")
            raise
    
    def extract_function_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract function calls from AI response.
        
        Args:
            response: AI response that may contain function calls
            
        Returns:
            List of function call dictionaries
        """
        function_calls = []
        
        try:
            # This is a simplified implementation
            # In practice, you'd parse the response format used by your AI agent
            
            # Example: Look for function call patterns
            import re
            
            # Pattern for function calls like: call_function(name="func_name", params={...})
            pattern = r'call_function\(name="([^"]+)",\s*params=(\{[^}]+\})\)'
            matches = re.findall(pattern, response)
            
            for match in matches:
                function_name, params_str = match
                try:
                    import json
                    params = json.loads(params_str)
                    function_calls.append({
                        "name": function_name,
                        "parameters": params
                    })
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse function parameters: {params_str}")
            
        except Exception as e:
            logger.warning(f"Error extracting function calls: {e}")
        
        return function_calls
    
    def validate_message_content(self, content: str, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate message content based on configuration rules.
        
        Args:
            content: Message content to validate
            config: Validation configuration
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            validation_config = config.get("validation", {})
            
            # Check minimum length
            min_length = validation_config.get("min_length", 0)
            if len(content) < min_length:
                return False, f"Content too short (minimum {min_length} characters)"
            
            # Check maximum length
            max_length = validation_config.get("max_length", float('inf'))
            if len(content) > max_length:
                return False, f"Content too long (maximum {max_length} characters)"
            
            # Check for required patterns
            required_patterns = validation_config.get("required_patterns", [])
            for pattern in required_patterns:
                import re
                if not re.search(pattern, content):
                    return False, f"Content missing required pattern: {pattern}"
            
            # Check for forbidden patterns
            forbidden_patterns = validation_config.get("forbidden_patterns", [])
            for pattern in forbidden_patterns:
                import re
                if re.search(pattern, content):
                    return False, f"Content contains forbidden pattern: {pattern}"
            
            return True, ""
            
        except Exception as e:
            logger.warning(f"Error validating message content: {e}")
            return True, ""  # Default to valid if validation fails
    
    async def create_ai_message(self, content: str, role: str = "assistant") -> AIMessage:
        """
        Create an AI message object.
        
        Args:
            content: Message content
            role: Message role (default: "assistant")
            
        Returns:
            AIMessage object
        """
        return AIMessage(
            role=role,
            content=content,
            timestamp=get_current_timestamp_num()
        )
    
    def parse_structured_response(self, response: str, expected_format: str) -> Dict[str, Any]:
        """
        Parse structured response based on expected format.
        
        Args:
            response: AI response to parse
            expected_format: Expected format (json, yaml, etc.)
            
        Returns:
            Parsed response as dictionary
        """
        try:
            if expected_format.lower() == "json":
                import json
                return json.loads(response)
            elif expected_format.lower() == "yaml":
                import yaml
                return yaml.safe_load(response)
            else:
                # For other formats, return as-is wrapped in a dict
                return {"content": response, "format": expected_format}
                
        except Exception as e:
            logger.warning(f"Error parsing structured response: {e}")
            return {"content": response, "error": str(e)}
