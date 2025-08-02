"""
UI function handler interface for AI Agents.

Defines the contract for handling UI function calls, including detection,
execution, and result formatting across different AI agent SDKs.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class UiFunctionHandlerInterface(ABC):
    """
    Abstract interface for UI function handling.
    
    Manages UI function detection, execution, and result formatting
    to ensure clean JSON output without explanatory text.
    """

    @abstractmethod
    def is_ui_function(self, tool_name: str) -> bool:
        """
        Check if a tool is a UI function.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool is a UI function, False otherwise
        """
        pass

    @abstractmethod
    def handle_ui_function(self, tool_name: str, kwargs: Dict[str, Any]) -> str:
        """
        Handle UI function call and return clean JSON output.
        
        Args:
            tool_name: Name of the UI function
            kwargs: Function arguments
            
        Returns:
            Clean JSON string for UI function result
        """
        pass

    @abstractmethod
    def extract_ui_function_names(self, tools: List[Dict[str, Any]]) -> List[str]:
        """
        Extract UI function names from tool definitions.
        
        Args:
            tools: List of tool definitions
            
        Returns:
            List of UI function names
        """
        pass

    @abstractmethod
    def extract_ui_function_from_result(self, result: Any) -> Optional[str]:
        """
        Extract UI function result from agent execution result.
        
        Args:
            result: Agent execution result
            
        Returns:
            UI function JSON string if found, None otherwise
        """
        pass

    @abstractmethod
    def is_ui_function_json(self, response: str) -> bool:
        """
        Check if a response is a direct UI function JSON.
        
        Args:
            response: Response string to check
            
        Returns:
            True if response is UI function JSON, False otherwise
        """
        pass

    @abstractmethod
    def enhance_ui_function_description(self, description: str) -> str:
        """
        Enhance tool description for UI functions with special instructions.
        
        Args:
            description: Original tool description
            
        Returns:
            Enhanced description with UI function instructions
        """
        pass
