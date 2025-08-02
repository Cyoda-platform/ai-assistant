"""
Tool adapter implementation for Google ADK Agent.

Provides concrete implementation for converting JSON tool definitions to
Google ADK FunctionTool objects and handling tool execution.
"""

import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Callable, Union, TYPE_CHECKING

try:
    from google.adk.tools import FunctionTool
    ADK_AVAILABLE = True
except ImportError:
    FunctionTool = Any
    ADK_AVAILABLE = False

if TYPE_CHECKING:
    from common.ai.interfaces.ui_function_handler import UiFunctionHandlerInterface

from common.ai.interfaces.tool_adapter import ToolAdapterInterface

logger = logging.getLogger(__name__)


class AdkToolAdapter(ToolAdapterInterface):
    """
    Concrete implementation of tool format adaptation and execution for Google ADK.
    
    Handles conversion between JSON tool definitions and Google ADK
    FunctionTool objects, with proper validation and execution.
    """

    def __init__(self, ui_function_handler: "UiFunctionHandlerInterface"):
        """
        Initialize tool adapter with UI function handler.
        
        Args:
            ui_function_handler: Handler for UI function operations
        """
        self.ui_function_handler = ui_function_handler

    def create_function_tools(self, tools: List[Dict[str, Any]], 
                             context: Any) -> List[FunctionTool]:
        """
        Convert JSON tool definitions to Google ADK FunctionTool objects.
        
        Args:
            tools: List of JSON tool definitions
            context: Execution context for dependency injection
            
        Returns:
            List of FunctionTool objects
        """
        if not ADK_AVAILABLE:
            logger.error("Google ADK not available")
            return []

        function_tools = []

        for tool in tools or []:
            if not self.validate_tool_definition(tool):
                continue

            function_def = tool.get("function", {})
            tool_name = function_def.get("name")
            
            # Create the tool function with proper error handling
            tool_function = self._create_tool_function(tool_name, context)
            
            # Create FunctionTool with enhanced configuration
            function_tool = self._build_function_tool(function_def, tool_function)
            
            if function_tool:
                function_tools.append(function_tool)
                logger.debug(f"Created ADK function tool: {tool_name}")

        logger.info(f"Created {len(function_tools)} ADK function tools")
        return function_tools

    def create_function_tool_from_json(self, tool_json: Dict[str, Any],
                                      on_invoke_tool: Callable) -> Optional[FunctionTool]:
        """
        Create a single FunctionTool from JSON definition for Google ADK.
        
        Args:
            tool_json: JSON tool definition
            on_invoke_tool: Function to handle tool invocation
            
        Returns:
            FunctionTool object or None if invalid
        """
        if not ADK_AVAILABLE:
            logger.error("Google ADK not available")
            return None

        if not self.validate_tool_definition(tool_json):
            return None
            
        function_def = tool_json.get("function", {})
        tool_name = function_def.get("name")
        
        if not tool_name:
            logger.warning(f"Tool missing name: {tool_json}")
            return None
            
        description = function_def.get("description", f"Execute {tool_name}")
        params_schema = function_def.get("parameters", {"type": "object", "properties": {}})
        
        # Enhance description for UI functions
        if self.ui_function_handler.is_ui_function(tool_name):
            description = self.ui_function_handler.enhance_ui_function_description(description)
        
        # Google ADK FunctionTool creation
        return FunctionTool(
            name=tool_name,
            description=description,
            parameters=params_schema,  # ADK uses 'parameters' instead of 'params_json_schema'
            func=on_invoke_tool
        )

    def validate_tool_definition(self, tool: Dict[str, Any]) -> bool:
        """
        Validate that a tool definition is valid for Google ADK.
        
        Args:
            tool: Tool definition to validate
            
        Returns:
            True if tool definition is valid, False otherwise
        """
        if not isinstance(tool, dict):
            return False
            
        if tool.get("type") != "function":
            return False
            
        function_def = tool.get("function", {})
        if not isinstance(function_def, dict):
            return False
            
        tool_name = function_def.get("name")
        if not tool_name or not isinstance(tool_name, str):
            logger.warning(f"Tool missing or invalid name: {tool}")
            return False
            
        return True

    def parse_tool_arguments(self, args_json: str, tool_name: str) -> Union[Dict[str, Any], str]:
        """
        Parse and validate tool arguments from JSON string.
        
        Args:
            args_json: JSON string containing tool arguments
            tool_name: Name of the tool for error reporting
            
        Returns:
            Parsed arguments dictionary or error message string
        """
        try:
            kwargs = json.loads(args_json)
            if not isinstance(kwargs, dict):
                return f"Tool arguments must be a JSON object for {tool_name}"
            return kwargs
        except json.JSONDecodeError as e:
            return f"Invalid JSON arguments for {tool_name}: {e}"

    async def execute_function(self, tool_name: str, kwargs: Dict[str, Any], 
                              context: Any) -> str:
        """
        Execute a function with proper context injection for Google ADK.
        
        Args:
            tool_name: Name of the function to execute
            kwargs: Function arguments
            context: Execution context
            
        Returns:
            Function result as string
        """
        if not context.has_method(tool_name):
            raise ValueError(f"Function '{tool_name}' not found in available methods")

        # Inject required context parameters
        kwargs.update(context.get_context_params())

        method = context.get_method(tool_name)
        
        # Execute with proper async handling
        if asyncio.iscoroutinefunction(method):
            result = await method(context.cls_instance, **kwargs)
        else:
            result = method(context.cls_instance, **kwargs)

        return str(result)

    def _create_tool_function(self, tool_name: str, context: Any):
        """
        Create a tool function following Google ADK patterns.
        
        Args:
            tool_name: Name of the tool
            context: Execution context
            
        Returns:
            Async tool function for Google ADK
        """
        async def tool_function(args: Dict[str, Any]) -> str:
            """Tool function implementation following ADK best practices"""
            try:
                # Google ADK passes arguments as dict directly, not JSON string
                kwargs = args if isinstance(args, dict) else {}

                # Handle UI functions with clean JSON output
                if self.ui_function_handler.is_ui_function(tool_name):
                    return self.ui_function_handler.handle_ui_function(tool_name, kwargs)

                # Execute regular function with proper context
                return await self.execute_function(tool_name, kwargs, context)

            except Exception as e:
                logger.exception(f"Error executing ADK tool {tool_name}: {e}")
                return f"Tool execution failed: {str(e)}"

        return tool_function

    def _build_function_tool(self, function_def: Dict[str, Any], tool_function) -> Optional[FunctionTool]:
        """
        Build FunctionTool object with proper configuration for Google ADK.
        
        Args:
            function_def: Function definition from JSON
            tool_function: Tool function implementation
            
        Returns:
            FunctionTool object or None if creation fails
        """
        try:
            tool_name = function_def.get("name")
            description = function_def.get("description", f"Execute {tool_name}")
            
            # Enhanced description for UI functions
            if self.ui_function_handler.is_ui_function(tool_name):
                description = self.ui_function_handler.enhance_ui_function_description(description)

            # Get parameters schema with validation
            params_schema = function_def.get("parameters", {})
            if not isinstance(params_schema, dict):
                logger.warning(f"Invalid parameters schema for {tool_name}, using empty schema")
                params_schema = {"type": "object", "properties": {}}

            # Google ADK FunctionTool creation
            return FunctionTool(
                name=tool_name,
                description=description,
                parameters=params_schema,
                func=tool_function
            )
        except Exception as e:
            logger.exception(f"Error building ADK function tool for {function_def.get('name')}: {e}")
            return None
