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
    Simplified Google ADK-based AI Agent following ADK best practices.
    Focuses on simplicity and leverages ADK's built-in capabilities.
    """

    def __init__(self, max_calls=config.MAX_AI_AGENT_ITERATIONS, mcp_servers=None):
        """
        Initialize the Google ADK Agent.

        Args:
            max_calls: Maximum number of agent iterations
            mcp_servers: List of MCP server names to enable (optional)
        """
        self.max_calls = max_calls
        self.mcp_servers = mcp_servers or []
        self._sessions = {}  # Cache sessions per technical_id for context retention
        self._session_services = {}  # Cache session services per technical_id

    def adapt_messages(self, messages: List[AIMessage]) -> List[types.Content]:
        """
        Convert AIMessage objects to ADK-compatible Content format.
        Simplified version that focuses on the essential conversion.
        """
        adapted_messages = []
        for message in messages:
            if not isinstance(message, AIMessage):
                continue

            # Convert content to string
            if isinstance(message.content, list):
                text_content = " ".join(str(item) for item in message.content)
            else:
                text_content = str(message.content) if message.content else ""

            # Map role (ADK uses 'model' instead of 'assistant')
            role = message.role or 'user'
            if role == 'assistant':
                role = 'model'
            elif role not in ['user', 'model', 'system']:
                role = 'user'

            adapted_messages.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=text_content)]
                )
            )

        return adapted_messages

    def _create_function_tools(self, tools: List[Dict[str, Any]],
                              context: AdkAgentContext) -> List[Any]:
        """
        Convert JSON tool definitions to simple Python functions for ADK.
        ADK handles the complex wrapping automatically.
        """
        function_tools = []

        for tool in tools or []:
            if tool.get("type") != "function":
                continue

            func_def = tool.get("function", {})
            func_name = func_def.get("name")

            if not func_name:
                continue

            # Skip if function not available (unless it's a UI function)
            if func_name not in context.methods_dict and not func_name.startswith(const.UI_FUNCTION_PREFIX):
                logger.warning(f"Tool {func_name} not found in methods_dict")
                continue

            # Create a simple wrapper function following ADK patterns
            def create_tool_wrapper(name: str, description: str):
                def tool_function(*args, **kwargs) -> str:
                    """Simple tool wrapper for ADK - handles both args and kwargs"""
                    try:
                        # ADK may pass arguments in different ways, handle both
                        all_params = {}

                        # If we have positional args, try to parse as JSON (like OpenAI SDK)
                        if args and len(args) > 0:
                            try:
                                if isinstance(args[0], str):
                                    # Try to parse as JSON string
                                    parsed_args = json.loads(args[0])
                                    if isinstance(parsed_args, dict):
                                        all_params.update(parsed_args)
                                elif isinstance(args[0], dict):
                                    # Direct dict argument
                                    all_params.update(args[0])
                            except (json.JSONDecodeError, TypeError):
                                # If parsing fails, treat as regular args
                                pass

                        # Add any keyword arguments
                        all_params.update(kwargs)

                        logger.debug(f"Tool {name} called with params: {all_params}")

                        # Handle UI functions - return clean JSON without markers
                        if name.startswith(const.UI_FUNCTION_PREFIX):
                            logger.debug(f"Handling UI function: {name} with params: {all_params}")

                            # Add default parameters for common UI function requirements
                            ui_params = {
                                "type": const.UI_FUNCTION_PREFIX,
                                "function": name,
                                **all_params
                            }

                            # Add common default parameters if missing
                            if name == "ui_function_list_all_technical_users" and not all_params:
                                logger.warning(f"UI function {name} called without parameters, adding defaults")
                                ui_params.update({
                                    "method": "GET",
                                    "path": "/api/clients",
                                    "response_format": "text"
                                })
                            elif name == "ui_function_issue_technical_user" and not all_params:
                                logger.warning(f"UI function {name} called without parameters, adding defaults")
                                ui_params.update({
                                    "method": "POST",
                                    "path": "/api/users",
                                    "response_format": "json"
                                })

                            ui_json = json.dumps(ui_params)
                            logger.info(f"UI function {name} returning: {ui_json}")
                            return ui_json

                        # Execute regular function
                        if name in context.methods_dict:
                            method = context.methods_dict[name]
                            method_kwargs = {
                                'technical_id': context.technical_id,
                                'entity': context.entity,
                                **all_params
                            }

                            # Handle async methods
                            if asyncio.iscoroutinefunction(method):
                                # Run async method in new event loop if needed
                                try:
                                    loop = asyncio.get_event_loop()
                                    if loop.is_running():
                                        # Create new loop in thread
                                        import concurrent.futures
                                        with concurrent.futures.ThreadPoolExecutor() as executor:
                                            future = executor.submit(
                                                lambda: asyncio.run(method(context.cls_instance, **method_kwargs))
                                            )
                                            result = future.result()
                                    else:
                                        result = loop.run_until_complete(method(context.cls_instance, **method_kwargs))
                                except Exception:
                                    # Fallback to sync call
                                    result = method(context.cls_instance, **method_kwargs)
                            else:
                                result = method(context.cls_instance, **method_kwargs)

                            return str(result)
                        else:
                            return f"Method {name} not found"

                    except Exception as e:
                        logger.exception(f"Error executing tool {name}: {e}")
                        return f"Error executing {name}: {str(e)}"

                # Set function metadata for ADK
                tool_function.__name__ = name
                tool_function.__doc__ = description
                return tool_function

            # Create the function with enhanced description for UI functions
            description = func_def.get("description", f"Execute {func_name}")
            if func_name.startswith(const.UI_FUNCTION_PREFIX):
                # Get required parameters from schema
                parameters = func_def.get("parameters", {})
                required_params = parameters.get("required", [])
                properties = parameters.get("properties", {})

                param_descriptions = []
                for param in required_params:
                    param_info = properties.get(param, {})
                    param_type = param_info.get("type", "string")
                    param_desc = param_info.get("description", param)
                    param_enum = param_info.get("enum", [])

                    if param_enum:
                        param_descriptions.append(f"- {param} ({param_type}): {param_desc}. Must be one of: {param_enum}")
                    else:
                        param_descriptions.append(f"- {param} ({param_type}): {param_desc}")

                required_params_text = "\n".join(param_descriptions) if param_descriptions else "No required parameters"

                description = f"""{description}

CRITICAL UI FUNCTION INSTRUCTIONS:
- This is a UI function that returns JSON data
- You MUST call this function with ALL required parameters
- Required parameters:
{required_params_text}
- You MUST return ONLY the raw JSON output from this function
- Do NOT add any text before or after the JSON
- Example: Call with all required parameters, then return only the JSON result"""

            function_obj = create_tool_wrapper(func_name, description)
            function_tools.append(function_obj)
            logger.debug(f"Created function tool: {func_name}")

        logger.info(f"Created {len(function_tools)} function tools")
        return function_tools

    def _create_mcp_tools(self) -> List[Any]:
        """
        Create MCP tools from configured servers.
        """
        if not self.mcp_servers or not MCP_AVAILABLE:
            return []

        mcp_tools = []
        mcp_configs = {
            "test_server": {
                "command": ["python", "mcp_servers/test_server.py"],
                "description": "Test MCP server"
            },
            "filesystem": {
                "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                "args": ["/app/data"],
                "description": "File system operations"
            },
            "memory": {
                "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
                "description": "Memory storage"
            },
            "sqlite": {
                "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite"],
                "args": ["/app/data/workflow.db"],
                "description": "SQLite operations"
            }
        }

        for server_name in self.mcp_servers:
            if server_name in mcp_configs:
                config = mcp_configs[server_name]
                try:
                    mcp_tool = MCPTool(
                        command=config["command"],
                        args=config.get("args", []),
                        env=config.get("env", {})
                    )
                    mcp_tools.append(mcp_tool)
                    logger.info(f"Created MCP tool: {server_name}")
                except Exception as e:
                    logger.error(f"Failed to create MCP server {server_name}: {e}")

        return mcp_tools

    def _convert_json_schema_to_adk(self, json_schema: dict) -> Any:
        """
        Convert JSON schema to ADK schema format.
        ADK uses google.genai.types.Schema for output_schema.
        """
        try:
            # Create ADK Schema from JSON schema
            schema_kwargs = {
                'type': json_schema.get('type', 'OBJECT').upper()
            }

            if 'description' in json_schema:
                schema_kwargs['description'] = json_schema['description']

            if 'properties' in json_schema:
                properties = {}
                for prop_name, prop_def in json_schema['properties'].items():
                    prop_schema = types.Schema(
                        type=prop_def.get('type', 'string').upper(),
                        description=prop_def.get('description', '')
                    )
                    properties[prop_name] = prop_schema
                schema_kwargs['properties'] = properties

            if 'required' in json_schema:
                schema_kwargs['required'] = json_schema['required']

            return types.Schema(**schema_kwargs)

        except Exception as e:
            logger.warning(f"Failed to convert JSON schema to ADK schema: {e}")
            # Fallback: return a simple object schema
            return types.Schema(
                type='OBJECT',
                description='Response object'
            )

    def _sanitize_agent_name(self, technical_id: str) -> str:
        """Create a valid ADK agent name from technical_id."""
        # Replace invalid characters with underscores
        sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in technical_id)

        # Ensure it starts with a letter or underscore
        if sanitized and sanitized[0].isdigit():
            sanitized = f'agent_{sanitized}'
        elif not sanitized:
            sanitized = 'workflow_agent'

        return sanitized[:50]  # Limit length

    def _create_agent(self, tools: List[Any], model: Any,
                     instructions: str, technical_id: str,
                     response_format: Optional[Dict[str, Any]] = None) -> Agent:
        """Create a Google ADK Agent with simplified configuration."""
        try:
            # Extract model name from model parameter, default to Gemini
            model_name = getattr(model, 'model_name', 'gemini-2.0-flash')

            # ADK only supports Google/Gemini models, not OpenAI
            if model_name.startswith(('gpt-', 'o1-', 'text-')):
                logger.warning(f"OpenAI model {model_name} not supported by ADK, using gemini-2.0-flash")
                model_name = 'gemini-2.0-flash'
            elif not model_name.startswith(('gemini-', 'models/')):
                logger.warning(f"Unknown model {model_name}, using gemini-2.0-flash")
                model_name = 'gemini-2.0-flash'

            # ADK uses model name directly for Gemini models
            model_instance = model_name
            logger.info(f"Using ADK model: {model_name}")

            # Create model configuration with proper temperature and context retention
            generate_content_config = types.GenerateContentConfig(
                temperature=getattr(model, 'temperature', 0.7),  # Good temperature for natural responses
                max_output_tokens=getattr(model, 'max_tokens', 8192),  # Ensure sufficient output length
                top_p=getattr(model, 'top_p', 0.95),  # Good balance for coherent responses
                top_k=getattr(model, 'top_k', 40),  # Reasonable diversity
                # Add safety settings if available
                safety_settings=getattr(model, 'safety_settings', None)
            )

            logger.debug(f"Model config: temp={generate_content_config.temperature}, "
                        f"max_tokens={generate_content_config.max_output_tokens}, "
                        f"top_p={generate_content_config.top_p}")

            # Add MCP tools and create agent
            mcp_tools = self._create_mcp_tools()
            all_tools = tools + mcp_tools
            agent_name = self._sanitize_agent_name(technical_id)

            # Handle response format (output schema)
            agent_kwargs = {
                'model': model_instance,
                'name': agent_name,
                'description': 'Workflow assistant with tools and MCP support',
                'instruction': instructions,
                'generate_content_config': generate_content_config
            }

            # If response_format is specified, use output_schema (no tools allowed)
            if response_format and response_format.get("schema"):
                # Convert JSON schema to ADK schema format
                schema = response_format["schema"]
                agent_kwargs['output_schema'] = self._convert_json_schema_to_adk(schema)
                # Note: When output_schema is set, tools cannot be used
                logger.info(f"Using output_schema - tools disabled for structured response")
            else:
                # Normal mode with tools
                agent_kwargs['tools'] = all_tools

            agent = Agent(**agent_kwargs)

            logger.info(f"Created ADK Agent '{agent_name}' with {len(all_tools)} tools")
            logger.debug(f"Function tools: {[getattr(t, '__name__', 'unknown') for t in tools]}")
            logger.debug(f"MCP tools: {len(mcp_tools)}")
            logger.debug(f"Agent has tools: {hasattr(agent, 'tools') and agent.tools is not None}")

            # Log tool details for debugging
            if hasattr(agent, 'tools') and agent.tools:
                logger.debug(f"Agent tools count: {len(agent.tools)}")

            return agent

        except Exception as e:
            logger.exception(f"Error creating ADK Agent: {e}")
            raise

    async def _validate_with_schema(self, content: str, schema: dict,
                                   attempt: int, max_retries: int) -> tuple[Optional[str], Optional[str]]:
        """Validate response against JSON schema."""
        try:
            parsed = json.loads(content)
            jsonschema.validate(instance=parsed, schema=schema)
            return content, None
        except (json.JSONDecodeError, ValidationError) as e:
            error = str(e)[:100]  # Truncate long errors
            msg = f"Validation failed (attempt {attempt}/{max_retries}): {error}. Return valid JSON."
            return None, msg

    def _build_conversation_context(self, messages: List[types.Content]) -> types.Content:
        """Build conversation context for multi-message conversations."""
        if not messages:
            return types.Content(role='user', parts=[types.Part(text="Please help me.")])

        if len(messages) == 1:
            return messages[0]

        # Build comprehensive conversation context for better context retention
        conversation_parts = [
            "=== CONVERSATION CONTEXT ===",
            "CRITICAL: You MUST maintain context from this conversation history when responding.",
            "Do NOT ask the user to repeat information they have already provided.",
            "Use the information from previous messages to inform your current response.",
            ""
        ]

        # Add all previous messages with clear formatting
        for i, msg in enumerate(messages[:-1], 1):
            role_label = "USER" if msg.role == "user" else "ASSISTANT"
            text = ""
            if msg.parts:
                text = "".join(part.text or "" for part in msg.parts)
            conversation_parts.append(f"[{i}] {role_label}: {text}")

        # Add current message with emphasis
        latest_msg = messages[-1]
        latest_text = ""
        if latest_msg.parts:
            latest_text = "".join(part.text or "" for part in latest_msg.parts)

        conversation_parts.extend([
            "",
            "=== CURRENT REQUEST ===",
            f"USER: {latest_text}",
            "",
            "Please respond based on the full conversation context above."
        ])

        full_context = "\n".join(conversation_parts)
        logger.debug(f"Built conversation context with {len(messages)} messages, length: {len(full_context)}")
        return types.Content(role='user', parts=[types.Part(text=full_context)])

    async def _create_session(self, technical_id: str, session_service: Any) -> Any:
        """Create a session for this run_agent call."""
        try:
            import time
            # Create unique session ID to avoid conflicts
            session_id = f"session_{technical_id}_{int(time.time())}"

            session = await session_service.create_session(
                app_name="workflow_app",
                user_id="default_user",
                session_id=session_id
            )
            logger.debug(f"Created ADK session: {session_id}")
            return session
        except Exception as e:
            logger.exception(f"Error creating session: {e}")
            raise

    def _extract_ui_function_result(self, response: str) -> Optional[str]:
        """
        Extract UI function JSON from agent response using multiple patterns.
        Improved to match OpenAI SDK agent reliability.
        """
        import re

        # Multiple patterns for robust extraction
        patterns = [
            r'UI_FUNCTION_RESULT:(.+?):END_UI_FUNCTION',  # Primary pattern with markers
            r'(.+?):END_UI_FUNCTION',  # Secondary pattern for direct JSON
            r'"result":\s*"UI_FUNCTION_RESULT:(.+?):END_UI_FUNCTION"',  # Wrapped in result field
            r'"result":\s*"([^"]*\\{.*?\\"type\\":\s*\\"ui_function\\".*?\\}[^"]*)"',  # Escaped JSON in result
            r'(\{.*?"type":\s*"ui_function".*?\})',  # Direct JSON with ui_function type
            r'"UI_FUNCTION_RESULT:(.+?):END_UI_FUNCTION"'  # Quoted UI function result
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                ui_json = match.group(1).strip()
                try:
                    # Handle escaped JSON strings
                    if '\\' in ui_json:
                        # Unescape the JSON string
                        ui_json = ui_json.replace('\\"', '"').replace('\\\\', '\\')

                    # Validate it's proper JSON and contains ui_function type
                    parsed = json.loads(ui_json)
                    if parsed.get("type") == "ui_function":
                        logger.debug(f"Extracted UI function result using pattern: {pattern}")
                        return ui_json
                except json.JSONDecodeError:
                    continue

        return None

    def _is_ui_function_json(self, response: str) -> bool:
        """Check if the response is a direct UI function JSON."""
        try:
            response = response.strip()
            if response.startswith('{') and response.endswith('}'):
                parsed = json.loads(response)
                return (isinstance(parsed, dict) and
                       parsed.get("type") == "ui_function" and
                       "function" in parsed)
        except (json.JSONDecodeError, AttributeError):
            pass
        return False

    async def run_agent(self, methods_dict: Dict[str, Any], technical_id: str,
                       cls_instance: Any, entity: Any, tools: List[Dict[str, Any]],
                       model: Any, messages: List[AIMessage], tool_choice: str = "auto",
                       response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Simplified ADK agent runner that leverages ADK's built-in capabilities.
        """
        try:
            # Create context for tool execution
            context = AdkAgentContext(
                methods_dict=methods_dict,
                technical_id=technical_id,
                cls_instance=cls_instance,
                entity=entity
            )

            # Convert messages to ADK format
            adapted_messages = self.adapt_messages(messages)
            if not adapted_messages:
                return "Error: No valid messages provided"

            logger.info(f"Processing {len(messages)} input messages -> {len(adapted_messages)} adapted messages")
            logger.debug(f"Message roles: {[msg.role for msg in adapted_messages]}")

            # Log first and last message for context debugging
            if adapted_messages:
                first_msg = adapted_messages[0]
                last_msg = adapted_messages[-1]
                first_text = "".join(part.text or "" for part in first_msg.parts) if first_msg.parts else ""
                last_text = "".join(part.text or "" for part in last_msg.parts) if last_msg.parts else ""
                logger.debug(f"First message: {first_text[:100]}...")
                logger.debug(f"Last message: {last_text[:100]}...")

            # Create function tools
            function_tools = self._create_function_tools(tools, context)

            # Create instructions based on response format and UI functions
            has_ui_functions = any(
                tool.get("function", {}).get("name", "").startswith(const.UI_FUNCTION_PREFIX)
                for tool in (tools or []) if tool and tool.get("type") == "function"
            )

            if response_format and response_format.get("schema"):
                # When using output_schema, tools are disabled
                instructions = """You are a helpful assistant that provides structured responses.

Respond with a JSON object that matches the required schema. Use your knowledge to provide accurate information."""
            elif has_ui_functions:
                instructions = """You are a helpful assistant that can use tools to complete tasks.

CRITICAL INSTRUCTION FOR UI FUNCTIONS:
When you call a function that starts with 'ui_function_', you MUST return ONLY the raw JSON output from that function call. Do not add any explanatory text, confirmation messages, or additional content. Return the JSON exactly as provided by the function, nothing more, nothing less.

For regular functions, you may provide explanatory text as normal."""
            else:
                instructions = """You are a helpful assistant that can use tools to complete tasks.

IMPORTANT: Always maintain context from the conversation history. If the user has provided information in previous messages, remember and use that information in your responses. Do not ask users to repeat information they have already provided."""

            # Create local session service and session for this run
            session_service = InMemorySessionService()
            logger.debug(f"Created session service for run_agent call")

            # Create agent and session
            agent = self._create_agent(function_tools, model, instructions, technical_id, response_format)
            session = await self._create_session(technical_id, session_service)
            logger.info(f"Using session {session.id} for entire run_agent call")

            # Create runner with local session service
            runner = Runner(
                agent=agent,
                app_name="workflow_app",
                session_service=session_service
            )
            logger.debug(f"Created runner with session service")

            # Build conversation context from all messages
            if len(adapted_messages) > 1:
                new_message = self._build_conversation_context(adapted_messages)
                logger.debug(f"Built conversation context from {len(adapted_messages)} messages")
            elif adapted_messages:
                new_message = adapted_messages[0]
                logger.debug("Using single message")
            else:
                new_message = types.Content(role='user', parts=[types.Part(text="Please help me.")])

            # Log what we're sending to the model for debugging
            if hasattr(new_message, 'parts') and new_message.parts:
                message_text = "".join(part.text or "" for part in new_message.parts)
                logger.info(f"Sending to ADK model: {message_text[:200]}...")
                logger.debug(f"Full message length: {len(message_text)} characters")

            # Run agent and collect response
            logger.info(f"Running ADK agent with {len(function_tools)} tools using session {session.id}")
            final_response = ""
            async for event in runner.run_async(
                user_id="default_user",
                session_id=session.id,
                new_message=new_message
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            final_response += part.text

                if event.is_final_response():
                    break

            response = final_response or "Task completed successfully."
            logger.info(f"ADK agent completed successfully")
            logger.debug(f"ADK response: {response[:200]}...")

            # Check for UI function result - try direct JSON parsing first
            ui_function_result = self._extract_ui_function_result(response)
            if ui_function_result:
                logger.debug(f"Extracted UI function result: {ui_function_result}")
                return ui_function_result

            # Also check if the response itself is a UI function JSON
            if self._is_ui_function_json(response):
                logger.debug("Response is direct UI function JSON")
                return response.strip()

            # When using output_schema, ADK handles validation automatically
            # No additional validation needed
            return response

        except Exception as e:
            logger.exception(f"Error in ADK agent execution: {e}")
            return f"Agent execution error: {str(e)}"

        finally:
            # Session service and session are local variables - automatic cleanup
            logger.debug(f"Session cleanup completed for session {session.id if 'session' in locals() else 'unknown'} (local variables)")

    async def _handle_schema_validation(self, response: str, schema: dict,
                                       agent: Agent, session: Any, runner: Runner) -> str:
        """Handle schema validation with retries."""
        for attempt in range(1, self.max_calls + 1):
            valid_str, error = await self._validate_with_schema(
                response, schema, attempt, self.max_calls
            )
            if valid_str is not None:
                return valid_str

            if attempt < self.max_calls:
                try:
                    # Ask for correction
                    correction_message = types.Content(
                        role='user',
                        parts=[types.Part(text=f"Validation error: {error}")]
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
                    logger.exception(f"Error during validation retry: {e}")
                    break

        raise Exception(f"Schema validation failed after {self.max_calls} attempts")

    async def cleanup(self):
        """Clean up resources. ADK handles most cleanup automatically."""
        try:
            logger.debug("ADK agent cleanup completed")
        except Exception as e:
            logger.exception(f"Error during cleanup: {e}")
