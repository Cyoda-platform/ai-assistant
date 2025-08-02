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
    import inspect
    from typing import Literal
    ADK_AVAILABLE = True
except ImportError:
    inspect = Any
    Literal = Any
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
                             context: Any) -> List[Any]:
        """
        Convert JSON tool definitions to ADK-compatible functions.

        ADK doesn't use FunctionTool objects - it uses regular Python functions
        that it wraps automatically.

        Args:
            tools: List of JSON tool definitions
            context: Execution context for dependency injection

        Returns:
            List of function objects that ADK can use directly
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

            # Allow UI functions even if they're not in methods_dict
            if (tool_name not in context.methods_dict and
                not self.ui_function_handler.is_ui_function(tool_name)):
                logger.warning(f"Tool {tool_name} not found in methods_dict")
                continue

            # Create ADK-compatible function using proper patterns
            function_tool = self._create_adk_function(function_def, context)

            if function_tool:
                function_tools.append(function_tool)
                logger.debug(f"Created ADK function: {tool_name}")

        logger.info(f"Created {len(function_tools)} ADK functions")
        return function_tools

    def create_function_tool_from_json(self, tool_json: Dict[str, Any],
                                      on_invoke_tool: Callable) -> Optional[Any]:
        """
        Create a single function from JSON definition for Google ADK.

        Args:
            tool_json: JSON tool definition
            on_invoke_tool: Function to handle tool invocation

        Returns:
            Function object or None if invalid
        """
        if not ADK_AVAILABLE:
            logger.error("Google ADK not available")
            return None

        if not self.validate_tool_definition(tool_json):
            return None

        function_def = tool_json.get("function", {})

        # Create ADK-compatible function
        return self._create_adk_function(function_def, None)

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

    def _create_adk_function(self, function_def: Dict[str, Any], context: Any) -> Optional[Any]:
        """
        Create ADK-compatible function using proper ADK patterns.

        Args:
            function_def: Function definition from JSON
            context: Execution context

        Returns:
            Function object that ADK can use directly
        """
        try:
            tool_name = function_def.get("name")
            description = function_def.get("description", f"Execute {tool_name}")
            parameters = function_def.get("parameters", {"type": "object", "properties": {}})

            if not tool_name:
                logger.warning(f"Function missing name: {function_def}")
                return None

            # Extract parameter information from the JSON schema
            param_props = parameters.get("properties", {})
            required_params = parameters.get("required", [])

            # Build enhanced description with enum information
            enhanced_description = description
            enum_info = []
            for param_name, param_info in param_props.items():
                param_enum = param_info.get("enum")
                if param_enum:
                    enum_info.append(f"{param_name} must be one of: {param_enum}")

            if enum_info:
                enhanced_description += f"\n\nParameter constraints:\n" + "\n".join(f"- {info}" for info in enum_info)

            # Enhance description for UI functions
            if self.ui_function_handler.is_ui_function(tool_name):
                enhanced_description = self.ui_function_handler.enhance_ui_function_description(enhanced_description)

            # Create parameter list for the function signature
            sig_params = []
            for param_name, param_info in param_props.items():
                param_type = param_info.get("type", "string")
                param_enum = param_info.get("enum")

                # Determine annotation based on type
                if param_type == "string":
                    annotation = str
                elif param_type == "integer":
                    annotation = int
                elif param_type == "number":
                    annotation = float
                elif param_type == "boolean":
                    annotation = bool
                else:
                    annotation = str

                # Handle enum constraints
                if param_enum:
                    try:
                        if len(param_enum) == 1:
                            annotation = Literal[param_enum[0]]
                        else:
                            annotation = Literal[tuple(param_enum)]
                    except (ImportError, TypeError):
                        annotation = str
                    logger.debug(f"Parameter {param_name} has enum constraint: {param_enum}")

                # Create parameter with proper annotation
                if param_name in required_params:
                    param = inspect.Parameter(param_name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=annotation)
                else:
                    param = inspect.Parameter(param_name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=annotation, default=None)
                sig_params.append(param)

            # Create the function signature
            sig = inspect.Signature(sig_params, return_annotation=str)

            # Create the actual function
            def tool_function(*args, **kwargs) -> str:
                """Dynamically created tool function for ADK"""
                try:
                    # Bind arguments to parameters
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()

                    logger.debug(f"Tool {tool_name} called with args: {bound_args.arguments}")

                    # Handle UI functions with special handling
                    if self.ui_function_handler.is_ui_function(tool_name):
                        logger.debug(f"Handling UI function: {tool_name}")
                        return self.ui_function_handler.handle_ui_function(tool_name, bound_args.arguments)

                    # Execute regular function
                    if context and context.has_method(tool_name):
                        # Inject context parameters
                        final_kwargs = bound_args.arguments.copy()
                        final_kwargs.update(context.get_context_params())

                        method = context.get_method(tool_name)
                        if asyncio.iscoroutinefunction(method):
                            # For async functions, we need to handle them properly
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    # If we're already in an async context, we can't use run_until_complete
                                    # Instead, we'll need to await this properly
                                    logger.warning(f"Async function {tool_name} called from sync context, this may cause issues")
                                    # Create a new event loop in a thread for this case
                                    import concurrent.futures
                                    with concurrent.futures.ThreadPoolExecutor() as executor:
                                        future = executor.submit(asyncio.run, method(context.cls_instance, **final_kwargs))
                                        result = future.result()
                                else:
                                    result = loop.run_until_complete(method(context.cls_instance, **final_kwargs))
                            except RuntimeError:
                                # No event loop, create one
                                result = asyncio.run(method(context.cls_instance, **final_kwargs))
                        else:
                            result = method(context.cls_instance, **final_kwargs)

                        return str(result)
                    else:
                        return f"Function '{tool_name}' not found or no context provided"

                except Exception as e:
                    logger.exception(f"Error executing ADK tool {tool_name}: {e}")
                    return f"Tool execution failed: {str(e)}"

            # Set function metadata for ADK
            tool_function.__name__ = tool_name
            tool_function.__doc__ = enhanced_description
            tool_function.__signature__ = sig

            logger.debug(f"Created ADK function: {tool_name} with signature: {sig}")
            return tool_function

        except Exception as e:
            logger.exception(f"Error creating ADK function for {function_def.get('name')}: {e}")
            return None
