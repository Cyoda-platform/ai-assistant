"""
UI function handler implementation for Google ADK Agent.

Provides concrete implementation for handling UI function calls, including
detection, execution, and result formatting specific to Google ADK.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, List

import common.config.const as const
from common.ai.interfaces.ui_function_handler import UiFunctionHandlerInterface

logger = logging.getLogger(__name__)


class AdkUiFunctionHandler(UiFunctionHandlerInterface):
    """
    Concrete implementation of UI function handling for Google ADK.
    
    Manages UI function detection, execution, and result formatting
    to ensure clean JSON output without explanatory text.
    """

    def is_ui_function(self, tool_name: str) -> bool:
        """
        Check if a tool is a UI function.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool is a UI function, False otherwise
        """
        return tool_name.startswith(const.UI_FUNCTION_PREFIX)

    def handle_ui_function(self, tool_name: str, kwargs: Dict[str, Any]) -> str:
        """
        Handle UI function call and return clean JSON output for Google ADK.
        
        Args:
            tool_name: Name of the UI function
            kwargs: Function arguments
            
        Returns:
            Clean JSON string for UI function result
        """
        logger.debug(f"Handling ADK UI function: {tool_name}")
        
        ui_json = json.dumps({
            "type": const.UI_FUNCTION_PREFIX,
            "function": tool_name,
            **kwargs
        })
        
        # Convert to single quotes format as requested
        ui_json_single_quotes = ui_json.replace('"', "'")
        logger.debug(f"ADK UI function JSON: {ui_json_single_quotes}")
        return ui_json_single_quotes

    def extract_ui_function_names(self, tools: List[Dict[str, Any]]) -> List[str]:
        """
        Extract UI function names from tool definitions for Google ADK.
        
        Args:
            tools: List of tool definitions
            
        Returns:
            List of UI function names
        """
        ui_function_names = []
        
        for tool in tools or []:
            if tool.get("type") == "function":
                func_name = tool.get("function", {}).get("name", "")
                if self.is_ui_function(func_name):
                    ui_function_names.append(func_name)
        
        if ui_function_names:
            logger.debug(f"Found ADK UI functions: {ui_function_names}")
        
        return ui_function_names

    def extract_ui_function_from_result(self, result: Any) -> Optional[str]:
        """
        Extract UI function result from Google ADK agent execution result.
        
        Args:
            result: Agent execution result
            
        Returns:
            UI function JSON string if found, None otherwise
        """
        # Google ADK may have different result structure than OpenAI SDK
        # Check for tool calls in ADK result format
        if hasattr(result, 'tool_calls') and result.tool_calls:
            for call in result.tool_calls:
                if hasattr(call, 'name') and self.is_ui_function(call.name):
                    logger.debug(f"ADK execution stopped at UI function: {call.name}")
                    
                    # Parse arguments from ADK format
                    args = {}
                    if hasattr(call, 'arguments') and call.arguments:
                        if isinstance(call.arguments, dict):
                            args = call.arguments
                        elif isinstance(call.arguments, str):
                            try:
                                args = json.loads(call.arguments)
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse ADK UI function arguments: {call.arguments}")

                    # Create UI function JSON
                    ui_data = {"type": const.UI_FUNCTION_PREFIX, "function": call.name}
                    if isinstance(args, dict):
                        ui_data.update(args)

                    ui_json = json.dumps(ui_data)
                    ui_json_single_quotes = ui_json.replace('"', "'")
                    logger.debug(f"ADK UI function JSON: {ui_json_single_quotes}")
                    return ui_json_single_quotes

        # Check for UI function in response content
        if hasattr(result, 'content') and result.content:
            ui_result = self.extract_ui_function_result(str(result.content))
            if ui_result:
                return ui_result

        return None

    def is_ui_function_json(self, response: str) -> bool:
        """
        Check if a response is a direct UI function JSON.
        
        Args:
            response: Response string to check
            
        Returns:
            True if response is UI function JSON, False otherwise
        """
        try:
            response = response.strip()
            if response.startswith('{') and response.endswith('}'):
                parsed = json.loads(response)
                return (isinstance(parsed, dict) and
                       (parsed.get("type") == const.UI_FUNCTION_PREFIX or
                        str(parsed.get("function", "")).startswith(const.UI_FUNCTION_PREFIX)))
        except (json.JSONDecodeError, AttributeError):
            pass
        return False

    def enhance_ui_function_description(self, description: str) -> str:
        """
        Enhance tool description for UI functions with special instructions.
        
        Args:
            description: Original tool description
            
        Returns:
            Enhanced description with UI function instructions
        """
        return (f"{description} CRITICAL: This is a UI function. "
               "Return ONLY the raw JSON output from this function call. "
               "Do not add any explanatory text.")

    def extract_ui_function_result(self, response: str) -> Optional[str]:
        """
        Extract UI function JSON from agent response using pattern matching.
        
        Args:
            response: Agent response that may contain UI function result
            
        Returns:
            UI function JSON if found, None otherwise
        """
        # Look for UI function JSON patterns - comprehensive search
        patterns = [
            # Direct JSON patterns
            r'(\{[^{}]*"type":\s*"ui_function"[^{}]*\})',
            r'(\{[^{}]*"function":\s*"ui_function_[^"]*"[^{}]*\})',
            
            # JSON with nested content
            r'(\{.*?"type":\s*"ui_function".*?\})',
            r'(\{.*?"function":\s*"ui_function_.*?\})',
            
            # JSON that might be quoted or escaped
            r'"(\{[^"]*"type":\s*"ui_function"[^"]*\})"',
            r"'(\{[^']*'type':\s*'ui_function'[^']*\})'",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                ui_json = match.strip()
                try:
                    # Handle potential escaping
                    if '\\' in ui_json:
                        ui_json = ui_json.replace('\\"', '"').replace("\\'", "'")

                    # Validate it's proper JSON and contains ui_function
                    parsed = json.loads(ui_json)
                    if (parsed.get("type") == const.UI_FUNCTION_PREFIX or
                            str(parsed.get("function", "")).startswith(const.UI_FUNCTION_PREFIX)):
                        logger.debug(f"Extracted ADK UI function result using pattern: {pattern}")
                        logger.debug(f"Extracted JSON: {ui_json}")
                        return ui_json
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON decode error for '{ui_json}': {e}")
                    continue

        # Fallback: try to find any JSON-like structure and check if it's a UI function
        json_pattern = r'\{[^{}]*\}'
        json_matches = re.findall(json_pattern, response)
        for json_match in json_matches:
            try:
                parsed = json.loads(json_match)
                if (isinstance(parsed, dict) and
                    (parsed.get("type") == const.UI_FUNCTION_PREFIX or
                     str(parsed.get("function", "")).startswith(const.UI_FUNCTION_PREFIX))):
                    logger.debug(f"Found ADK UI function JSON in fallback search: {json_match}")
                    return json_match
            except json.JSONDecodeError:
                continue

        return None
