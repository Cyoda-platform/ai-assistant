"""
Tool adapter interface for AI Agents.

Defines the contract for converting tool definitions to agent-specific
tool objects and handling tool execution across different AI agent SDKs.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable, Union


class ToolAdapterInterface(ABC):
    """
    Abstract interface for tool format adaptation and execution.
    
    Handles conversion between JSON tool definitions and agent-specific
    tool objects, including tool validation and execution.
    """

    @abstractmethod
    def create_function_tools(self, tools: List[Dict[str, Any]],
                             context: Any) -> List[Any]:
        """
        Convert JSON tool definitions to agent-specific tool objects.

        Args:
            tools: List of JSON tool definitions
            context: Execution context for dependency injection

        Returns:
            List of agent-specific tool objects (FunctionTool for OpenAI, functions for ADK)
        """
        pass

    @abstractmethod
    def create_function_tool_from_json(self, tool_json: Dict[str, Any],
                                      on_invoke_tool: Callable) -> Optional[Any]:
        """
        Create a single tool from JSON definition.
        
        Args:
            tool_json: JSON tool definition
            on_invoke_tool: Function to handle tool invocation
            
        Returns:
            Agent-specific tool object or None if invalid
        """
        pass

    @abstractmethod
    def validate_tool_definition(self, tool: Dict[str, Any]) -> bool:
        """
        Validate that a tool definition is valid.
        
        Args:
            tool: Tool definition to validate
            
        Returns:
            True if tool definition is valid, False otherwise
        """
        pass

    @abstractmethod
    def parse_tool_arguments(self, args_json: str, tool_name: str) -> Union[Dict[str, Any], str]:
        """
        Parse and validate tool arguments from JSON string.
        
        Args:
            args_json: JSON string containing tool arguments
            tool_name: Name of the tool for error reporting
            
        Returns:
            Parsed arguments dictionary or error message string
        """
        pass

    @abstractmethod
    async def execute_function(self, tool_name: str, kwargs: Dict[str, Any], 
                              context: Any) -> str:
        """
        Execute a function with proper context injection.
        
        Args:
            tool_name: Name of the function to execute
            kwargs: Function arguments
            context: Execution context
            
        Returns:
            Function result as string
        """
        pass
