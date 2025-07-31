import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
import os

import jsonschema
from jsonschema import ValidationError

# Google ADK imports
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

# Try to import MCPTool, but handle gracefully if not available
try:
    from google.adk.tools.mcp_tool import MCPTool
    MCP_AVAILABLE = True
except ImportError:
    MCPTool = None
    MCP_AVAILABLE = False

from common.config import const
from common.config.config import config
from entity.model import AIMessage

logger = logging.getLogger(__name__)


class AdkAgentContext:
    """Context object for dependency injection in Google ADK"""

    def __init__(self, methods_dict: Dict[str, Any], technical_id: str,
                 cls_instance: Any, entity: Any):
        self.methods_dict = methods_dict or {}
        self.technical_id = technical_id
        self.cls_instance = cls_instance
        self.entity = entity


class AdkAgent:
    """
    Google ADK-based AI Agent using modern ADK patterns and best practices.
    Supports both OpenAI models (via LiteLlm) and Gemini models with proper
    agent configuration, tool management, and session handling.
    """

    def __init__(self, max_calls=config.MAX_AI_AGENT_ITERATIONS, mcp_servers=None):
        """
        Initialize the Google ADK Agent.

        Args:
            max_calls: Maximum number of agent iterations
            mcp_servers: List of MCP server names to enable (optional)
        """
        self.max_calls = max_calls
        self.session_service = InMemorySessionService()
        self.mcp_servers = mcp_servers or []
        self._agent_cache = {}
        self._session_cache = {}

    def adapt_messages(self, messages: List[AIMessage]) -> List[types.Content]:
        """
        Convert AIMessage objects to ADK-compatible Content format.

        Args:
            messages: List of AIMessage objects

        Returns:
            List of types.Content objects
        """
        adapted_messages = []
        for message in messages:
            if isinstance(message, AIMessage):
                content = message.content
                if content:
                    # Convert to ADK Content format
                    text_content = " ".join(content) if isinstance(content, list) else content
                    adapted_messages.append(
                        types.Content(
                            role=message.role or 'user',
                            parts=[types.Part(text=text_content)]
                        )
                    )
            else:
                logger.warning(f"Unexpected message type: {type(message)}")
        return adapted_messages

    def _create_function_tools(self, tools: List[Dict[str, Any]],
                              context: AdkAgentContext) -> List[Any]:
        """
        Convert JSON tool definitions to ADK-compatible functions using proper ADK patterns.

        According to ADK docs, functions should be passed directly to the tools list,
        not wrapped in FunctionTool manually. ADK will handle the wrapping automatically.

        Args:
            tools: List of tool definitions in JSON format
            context: Agent context for dependency injection

        Returns:
            List of function objects that ADK can use directly
        """
        function_tools = []

        for tool in tools or []:
            if tool.get("type") == "function":
                func_def = tool.get("function", {})
                func_name = func_def.get("name")

                if not func_name:
                    logger.warning(f"Tool missing name: {tool}")
                    continue

                # Allow UI functions even if they're not in methods_dict
                if func_name not in context.methods_dict and not func_name.startswith(const.UI_FUNCTION_PREFIX):
                    logger.warning(f"Tool {func_name} not found in methods_dict")
                    continue

                # Create ADK-compatible function using proper patterns
                def create_tool_function(name: str, description: str, parameters: dict):
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

                    # Create a wrapper function that calls the actual method
                    def create_wrapper():
                        # Build the function signature dynamically
                        import inspect

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

                            # Handle enum constraints - create a custom type hint for better ADK understanding
                            if param_enum:
                                # For enum parameters, we'll use a Union type or Literal for better type hints
                                try:
                                    from typing import Literal
                                    # Create a Literal type with the enum values
                                    if len(param_enum) == 1:
                                        # Single enum value - use Literal
                                        annotation = Literal[param_enum[0]]
                                    else:
                                        # Multiple enum values - use Literal with all values
                                        annotation = Literal[tuple(param_enum)]
                                except ImportError:
                                    # Fallback if Literal is not available
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

                                logger.debug(f"Tool {name} called with args: {bound_args.arguments}")

                                # Check if this is a UI function that needs special handling
                                if name.startswith(const.UI_FUNCTION_PREFIX):
                                    logger.debug(f"Handling UI function: {name}")
                                    # For UI functions, return JSON directly
                                    ui_json = json.dumps({
                                        "type": const.UI_FUNCTION_PREFIX,
                                        "function": name,
                                        **bound_args.arguments
                                    })
                                    return ui_json

                                # Validate enum constraints for regular functions
                                for param_name, param_value in bound_args.arguments.items():
                                    if param_value is not None:  # Skip validation for None values
                                        param_info = param_props.get(param_name, {})
                                        param_enum = param_info.get("enum")
                                        if param_enum and param_value not in param_enum:
                                            error_msg = f"Parameter '{param_name}' value '{param_value}' is not valid. Must be one of: {param_enum}"
                                            logger.error(error_msg)
                                            return f"Error: {error_msg}"

                                # Add required parameters that the method expects
                                method_kwargs = {
                                    'technical_id': context.technical_id,
                                    'entity': context.entity,
                                    **bound_args.arguments  # Include all parameters passed by ADK
                                }

                                logger.debug(f"Calling method {name} with: {method_kwargs}")

                                # Execute the method (only for non-UI functions)
                                if name in context.methods_dict:
                                    method = context.methods_dict[name]
                                    if asyncio.iscoroutinefunction(method):
                                        # Handle async methods - run them synchronously for ADK
                                        try:
                                            loop = asyncio.get_event_loop()
                                            if loop.is_running():
                                                # We're already in an async context
                                                import concurrent.futures

                                                def run_async():
                                                    new_loop = asyncio.new_event_loop()
                                                    asyncio.set_event_loop(new_loop)
                                                    try:
                                                        return new_loop.run_until_complete(method(context.cls_instance, **method_kwargs))
                                                    finally:
                                                        new_loop.close()

                                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                                    future = executor.submit(run_async)
                                                    result = future.result()
                                            else:
                                                result = loop.run_until_complete(method(context.cls_instance, **method_kwargs))
                                        except Exception as async_error:
                                            logger.warning(f"Async execution failed, trying sync: {async_error}")
                                            # Fallback: try to call it synchronously (might fail)
                                            result = method(context.cls_instance, **method_kwargs)
                                    else:
                                        result = method(context.cls_instance, **method_kwargs)
                                else:
                                    # This should not happen for regular functions, but handle gracefully
                                    result = f"Method {name} not found in methods_dict"

                                logger.info(f"Tool {name} executed successfully: {result}")
                                return str(result)

                            except Exception as e:
                                logger.exception(f"Error executing tool {name}: {e}")
                                return f"Error executing {name}: {str(e)}"

                        # Set function metadata for ADK (this is crucial!)
                        tool_function.__name__ = name
                        tool_function.__doc__ = enhanced_description  # Use enhanced description with enum info
                        tool_function.__signature__ = sig

                        return tool_function

                    return create_wrapper()

                # Enhance description for UI functions
                original_description = func_def.get("description", f"Execute {func_name}")
                if func_name.startswith(const.UI_FUNCTION_PREFIX):
                    enhanced_description = f"{original_description} CRITICAL: This is a UI function. Return ONLY the raw JSON output from this function call. Do not add any explanatory text."
                else:
                    enhanced_description = original_description

                # Create the function and add it directly (ADK will wrap it automatically)
                func_parameters = func_def.get("parameters", {})
                function_obj = create_tool_function(func_name, enhanced_description, func_parameters)
                function_tools.append(function_obj)
                logger.debug(f"Created ADK function: {func_name}")

        return function_tools

    def _create_mcp_tools(self) -> List[Any]:
        """
        Create MCP tools from configured servers using ADK patterns.

        Returns:
            List of MCP tool objects
        """
        if not self.mcp_servers:
            return []

        mcp_tools = []

        # Predefined MCP server configurations
        mcp_configs = {
            "test_server": {
                "command": ["python", "mcp_servers/test_server.py"],
                "description": "Test MCP server with sample functions"
            },
            "filesystem": {
                "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                "args": ["/app/data"],
                "description": "File system operations"
            },
            "memory": {
                "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
                "description": "Persistent memory storage"
            },
            "sqlite": {
                "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite"],
                "args": ["/app/data/workflow.db"],
                "description": "SQLite database operations"
            }
        }

        for server_name in self.mcp_servers:
            if server_name in mcp_configs:
                config = mcp_configs[server_name]
                try:
                    if MCP_AVAILABLE:
                        # Create actual MCPTool instance using ADK patterns
                        mcp_tool = MCPTool(
                            command=config["command"],
                            args=config.get("args", []),
                            env=config.get("env", {})
                        )
                        mcp_tools.append(mcp_tool)
                        logger.info(f"Created ADK MCPTool for server: {server_name}")
                    else:
                        logger.warning(f"MCP not available, skipping server: {server_name}")

                    logger.debug(f"  Command: {config['command']}")
                    logger.debug(f"  Description: {config['description']}")

                except Exception as e:
                    logger.error(f"Failed to configure MCP server {server_name}: {e}")
            else:
                logger.warning(f"Unknown MCP server: {server_name}")

        logger.info(f"Configured {len(mcp_tools)} MCP servers")
        return mcp_tools

    def _sanitize_agent_name(self, technical_id: str) -> str:
        """
        Sanitize technical_id to create a valid ADK agent name.

        ADK agent names must be valid Python identifiers:
        - Start with letter or underscore
        - Contain only letters, digits, and underscores
        - No hyphens or other special characters

        Args:
            technical_id: Technical identifier (may contain hyphens, etc.)

        Returns:
            Sanitized agent name
        """
        # Replace hyphens and other invalid characters with underscores
        sanitized = technical_id.replace('-', '_').replace('.', '_')

        # Remove any other non-alphanumeric characters except underscores
        sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in sanitized)

        # Ensure it starts with a letter or underscore
        if sanitized and sanitized[0].isdigit():
            sanitized = f'agent_{sanitized}'
        elif not sanitized or not (sanitized[0].isalpha() or sanitized[0] == '_'):
            sanitized = f'workflow_agent_{sanitized}'

        # Ensure it's not empty and has a reasonable length
        if not sanitized:
            sanitized = 'workflow_agent'
        elif len(sanitized) > 50:  # Keep reasonable length
            sanitized = sanitized[:50]

        return sanitized

    def _create_agent(self, tools: List[Any], model: Any,
                     instructions: str, technical_id: str) -> Agent:
        """
        Create a Google ADK Agent using proper ADK patterns.

        Args:
            tools: List of function objects (ADK will wrap them automatically)
            model: Model configuration
            instructions: Agent instructions
            technical_id: Technical identifier for the agent

        Returns:
            Agent instance
        """
        try:
            # Extract model name
            # Determine the model name and configure for OpenAI if needed
            model_name = model.model_name if hasattr(model, 'model_name') else 'gemini-2.0-flash'

            # Configure model based on provider
            if model_name.startswith(('gpt-', 'o1-', 'text-')):
                # For OpenAI models, use LiteLlm wrapper
                if not os.getenv('OPENAI_API_KEY'):
                    logger.warning("OpenAI model specified but OPENAI_API_KEY not set")

                model_instance = LiteLlm(model=f"openai/{model_name}")
                logger.info(f"Using OpenAI model via LiteLlm: {model_name}")
            else:
                # For Gemini models, use model name directly
                model_instance = model_name
                logger.info(f"Using Gemini model: {model_name}")

            # Create GenerateContentConfig for model settings (crucial for response quality)
            generate_content_config = types.GenerateContentConfig(
                temperature=getattr(model, 'temperature', 0.7),
                max_output_tokens=getattr(model, 'max_tokens', None),
                top_p=getattr(model, 'top_p', None),
                top_k=getattr(model, 'top_k', None),
                # Add safety settings if available
                safety_settings=getattr(model, 'safety_settings', None)
            )

            # Add MCP tools
            mcp_tools = self._create_mcp_tools()
            all_tools = tools + mcp_tools

            # Create valid agent name from technical_id
            agent_name = self._sanitize_agent_name(technical_id)

            # Create ADK agent using proper configuration with model settings
            agent = Agent(
                model=model_instance,
                name=agent_name,
                description='Workflow assistant that can use tools to complete tasks and access external services via MCP.',
                instruction=instructions,
                tools=all_tools,
                generate_content_config=generate_content_config  # This is the key missing piece!
            )

            logger.info(f"Created ADK Agent '{agent_name}' with {len(all_tools)} tools ({len(tools)} function tools, {len(mcp_tools)} MCP tools)")
            logger.info(f"Model settings: temperature={generate_content_config.temperature}, max_tokens={generate_content_config.max_output_tokens}")
            logger.debug(f"Function tools: {[getattr(t, '__name__', 'unknown') for t in tools]}")
            return agent

        except Exception as e:
            logger.exception(f"Error creating ADK Agent: {e}")
            raise

    async def _validate_with_schema(self, content: str, schema: dict,
                                   attempt: int, max_retries: int) -> tuple[Optional[str], Optional[str]]:
        """
        Validate response against JSON schema.

        Args:
            content: Response content to validate
            schema: JSON schema for validation
            attempt: Current attempt number
            max_retries: Maximum number of retries

        Returns:
            Tuple of (validated_content, error_message)
        """
        try:
            parsed = json.loads(content)
            jsonschema.validate(instance=parsed, schema=schema)
            return content, None
        except (json.JSONDecodeError, ValidationError) as e:
            error = str(e)
            error = (error[:50] + '...') if len(error) > 50 else error
            msg = f"Validation failed on attempt {attempt}/{max_retries}: {error}. Please return correct JSON."
            if attempt > 2:
                msg = f"{msg} If the task is too complex, simplify but ensure valid JSON."
            return None, msg

    async def _create_session(self, technical_id: str, messages: List[types.Content] = None) -> Any:
        """
        Create or get session for conversation management using ADK patterns.

        Args:
            technical_id: Technical identifier for the session
            messages: Optional conversation history (for future use)

        Returns:
            Session instance
        """
        session_id = f"session_{technical_id}"

        # For manual conversation management, always create a fresh session
        if technical_id.endswith('_manual'):
            session_id = f"{session_id}_{len(messages) if messages else 0}"

        if session_id in self._session_cache:
            return self._session_cache[session_id]

        try:
            session = await self.session_service.create_session(
                app_name="workflow_app",
                user_id="default_user",
                session_id=session_id
            )

            self._session_cache[session_id] = session
            logger.debug(f"Created ADK session: {session_id}")
            return session

        except Exception as e:
            logger.exception(f"Error creating ADK session: {e}")
            raise

    def _convert_messages_to_input(self, messages: List[types.Content], use_session: bool = True) -> Union[types.Content, List[types.Content]]:
        """
        Convert messages to input format for ADK Runner.

        Args:
            messages: List of Content objects
            use_session: Whether to use session management or manual conversation history

        Returns:
            Input for the runner (latest message when using session, all messages when not)
        """
        if not messages:
            return types.Content(
                role='user',
                parts=[types.Part(text="Please help me.")]
            )

        if use_session:
            # ADK Runner expects the latest message as new_message
            # Previous conversation history is managed by the session
            return messages[-1]
        else:
            # For complex conversations, we need to provide full context
            # This is crucial for maintaining conversation quality
            return messages

    async def _handle_ui_functions(self, function_name: str, function_args: Dict[str, Any]) -> str:
        """
        Handle UI function calls that need special formatting.

        Args:
            function_name: Name of the UI function
            function_args: Function arguments

        Returns:
            Formatted UI function response
        """
        try:
            if function_name.startswith(const.UI_FUNCTION_PREFIX):
                return json.dumps({
                    "type": const.UI_FUNCTION_PREFIX,
                    "function": function_name,
                    **function_args
                })
            return f"Unknown UI function: {function_name}"

        except Exception as e:
            logger.exception(f"Error handling UI function {function_name}: {e}")
            return f"Error handling UI function {function_name}: {str(e)}"

    def _extract_ui_function_result(self, response: str) -> Optional[str]:
        """
        Extract UI function JSON from ADK agent response.

        Args:
            response: Agent response that may contain UI function result

        Returns:
            UI function JSON if found, None otherwise
        """
        import re

        # Look for UI function JSON patterns
        patterns = [
            r'(\{.*?"type":\s*"ui_function".*?\})',  # JSON with ui_function type
            r'(\{.*?"function":\s*"ui_function_.*?\})'  # JSON with ui_function_ in function name
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                ui_json = match.group(1).strip()
                try:
                    # Validate it's proper JSON and contains ui_function
                    parsed = json.loads(ui_json)
                    if (parsed.get("type") == "ui_function" or
                        str(parsed.get("function", "")).startswith("ui_function_")):
                        return ui_json
                except json.JSONDecodeError:
                    continue

        return None

    async def run_agent(self, methods_dict: Dict[str, Any], technical_id: str,
                       cls_instance: Any, entity: Any, tools: List[Dict[str, Any]],
                       model: Any, messages: List[AIMessage], tool_choice: str = "auto",
                       response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Main method to run the ADK agent using proper ADK patterns.

        Args:
            methods_dict: Dictionary of available methods/tools
            technical_id: Technical identifier for the session
            cls_instance: Class instance for method calls
            entity: Entity object for context
            tools: List of tool definitions
            model: Model configuration
            messages: List of AIMessage objects
            tool_choice: Tool choice strategy (not used in ADK, tools are always available)
            response_format: Optional response format with schema for validation

        Returns:
            Agent response as string
        """
        try:
            # Create context for dependency injection
            context = AdkAgentContext(
                methods_dict=methods_dict,
                technical_id=technical_id,
                cls_instance=cls_instance,
                entity=entity
            )

            # Convert messages to ADK format
            adapted_messages = self.adapt_messages(messages)

            # Create function tools from JSON definitions
            function_tools = self._create_function_tools(tools, context)

            # Create agent instructions with UI function support
            has_ui_functions = any(tool.get("function", {}).get("name", "").startswith(const.UI_FUNCTION_PREFIX)
                                 for tool in tools if tool.get("type") == "function")

            if has_ui_functions:
                instructions = """You are a helpful assistant that can use tools to complete tasks.

CRITICAL INSTRUCTION FOR UI FUNCTIONS:
When you call a function that starts with 'ui_function_', you MUST return ONLY the raw JSON output from that function call. Do not add any explanatory text, confirmation messages, or additional content. Return the JSON exactly as provided by the function, nothing more, nothing less.

For regular functions, you may provide explanatory text as normal."""
            else:
                instructions = "You are a helpful assistant that can use tools to complete tasks."

            # Create or get cached agent
            agent_key = f"agent_{technical_id}_{len(function_tools)}"
            if agent_key not in self._agent_cache:
                agent = self._create_agent(function_tools, model, instructions, technical_id)
                self._agent_cache[agent_key] = agent
            else:
                agent = self._agent_cache[agent_key]

            # Create session (always use session for ADK, but make it unique for each conversation)
            session = await self._create_session(technical_id, adapted_messages)

            # Create runner
            runner = Runner(
                agent=agent,
                app_name="workflow_app",
                session_service=self.session_service
            )

            # For multi-message conversations, we need to build up the conversation context
            # This is crucial for maintaining response quality comparable to OpenAI SDK
            if len(adapted_messages) > 1:
                # Add all previous messages to build conversation context
                for i, msg in enumerate(adapted_messages[:-1]):
                    try:
                        # Add each message to the conversation history
                        async for _ in runner.run_async(
                            user_id="default_user",
                            session_id=session.id,
                            new_message=msg
                        ):
                            break  # Just add to history, don't need full response
                    except Exception as e:
                        logger.warning(f"Failed to add message {i} to conversation history: {e}")

            # Convert messages to input format (always use latest message for ADK)
            new_message = self._convert_messages_to_input(adapted_messages, use_session=True)

            # Run the agent using ADK patterns
            logger.info(f"Running ADK agent with {len(function_tools)} tools")

            final_response = ""
            async for event in runner.run_async(
                user_id="default_user",
                session_id=session.id,
                new_message=new_message
            ):
                # Handle different event types
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            final_response += part.text
                        elif hasattr(part, 'function_call') and part.function_call:
                            # Handle UI functions specially
                            func_call = part.function_call
                            if func_call.name and func_call.name.startswith(const.UI_FUNCTION_PREFIX):
                                args = func_call.args or {}
                                return await self._handle_ui_functions(func_call.name, args)

                # Check for final response
                if event.is_final_response():
                    break

            response = final_response or "Task completed successfully."
            logger.info(f"ADK agent completed successfully")

            # Check if this is a UI function result that should return only JSON
            ui_function_result = self._extract_ui_function_result(response)
            if ui_function_result:
                logger.debug(f"Extracted UI function result: {ui_function_result}")
                return ui_function_result

            # Handle schema validation if required
            if response_format and response_format.get("schema"):
                response = await self._handle_schema_validation(
                    response, response_format["schema"], agent, session, runner
                )

            return response

        except Exception as e:
            logger.exception(f"Error in ADK agent execution: {e}")
            return f"Agent execution error: {str(e)}"

    async def _handle_schema_validation(self, response: str, schema: dict,
                                       agent: Agent, session: Any, runner: Runner) -> str:
        """
        Handle schema validation with retries using ADK patterns.

        Args:
            response: Initial response to validate
            schema: JSON schema for validation
            agent: Agent instance for retries
            session: Session for conversation continuity
            runner: Runner for executing retries

        Returns:
            Validated response
        """
        for attempt in range(1, self.max_calls + 1):
            valid_str, error = await self._validate_with_schema(
                response, schema, attempt, self.max_calls
            )
            if valid_str is not None:
                return valid_str

            # If validation failed, retry with correction
            logger.warning(f"Schema validation failed on attempt {attempt}: {error}")

            if attempt < self.max_calls:
                try:
                    correction_message = types.Content(
                        role='user',
                        parts=[types.Part(text=f"The previous response had validation errors: {error}")]
                    )

                    correction_response = ""
                    async for event in runner.run_async(
                        user_id="default_user",
                        session_id=session.id,
                        new_message=correction_message
                    ):
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    correction_response += part.text

                        if event.is_final_response():
                            break

                    response = correction_response

                except Exception as e:
                    logger.exception(f"Error during validation retry {attempt}: {e}")
                    break

        # If all retries failed
        raise Exception(f"Schema validation failed after {self.max_calls} attempts. Last response: {response}")

    async def cleanup(self):
        """
        Clean up resources using ADK patterns.

        Note: ADK handles most cleanup automatically,
        but we can clear our caches.
        """
        try:
            # Clear agent cache
            self._agent_cache.clear()
            logger.debug("Cleared agent cache")

            # Clear session cache
            self._session_cache.clear()
            logger.debug("Cleared session cache")

        except Exception as e:
            logger.exception(f"Error during cleanup: {e}")

    def __del__(self):
        """
        Destructor to ensure cleanup.

        Note: ADK manages resources automatically,
        so minimal cleanup is needed.
        """
        try:
            # Clear caches
            if hasattr(self, '_agent_cache'):
                self._agent_cache.clear()
            if hasattr(self, '_session_cache'):
                self._session_cache.clear()
        except:
            pass
