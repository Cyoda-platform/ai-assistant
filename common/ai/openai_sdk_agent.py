import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Type
import os

try:
    import jsonschema
    from jsonschema import ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    jsonschema = None
    ValidationError = Exception
    JSONSCHEMA_AVAILABLE = False

from pydantic import BaseModel

# OpenAI Agents SDK imports
from agents import (
    Agent, Runner, function_tool, FunctionTool, ModelSettings,
    AgentsException, MaxTurnsExceeded, ModelBehaviorError, RunConfig
)
from agents.tool_context import ToolContext

from common.config import const
from common.config.config import config
from entity.model import AIMessage

logger = logging.getLogger(__name__)


class OpenAiSdkAgentContext:
    """Context object for dependency injection in OpenAI Agents SDK"""

    def __init__(self, methods_dict: Dict[str, Any], technical_id: str,
                 cls_instance: Any, entity: Any):
        self.methods_dict = methods_dict or {}
        self.technical_id = technical_id
        self.cls_instance = cls_instance
        self.entity = entity


class OpenAiSdkAgent:
    """
    Simplified OpenAI Agents SDK-based AI Agent following modern best practices.
    Maintains JSON tools format and existing run_agent signature while using
    clean, maintainable patterns from the OpenAI Agents SDK documentation.
    """

    def __init__(self, max_calls=config.MAX_AI_AGENT_ITERATIONS):
        """
        Initialize the OpenAI SDK Agent.

        Args:
            max_calls: Maximum number of agent iterations (max_turns in SDK)
        """
        self.max_calls = max_calls

    def _create_function_tools(self, tools: List[Dict[str, Any]],
                              context: OpenAiSdkAgentContext) -> List[FunctionTool]:
        """
        Convert JSON tool definitions to OpenAI Agents SDK FunctionTool objects.
        Simplified version following OpenAI Agents SDK best practices.
        """
        function_tools = []

        for tool in tools or []:
            if tool.get("type") != "function":
                continue

            function_def = tool.get("function", {})
            tool_name = function_def.get("name")

            if not tool_name:
                logger.warning(f"Tool missing name: {tool}")
                continue

            # Create simplified tool function
            def create_tool_function(name: str):
                async def tool_function(ctx: ToolContext, args_json: str) -> str:
                    """Simplified tool function following SDK best practices"""
                    try:
                        # Parse arguments
                        try:
                            kwargs = json.loads(args_json)
                        except json.JSONDecodeError as e:
                            return f"Invalid JSON arguments: {e}"

                        # Handle UI functions - return clean JSON directly
                        if name.startswith(const.UI_FUNCTION_PREFIX):
                            logger.debug(f"Handling UI function: {name}")
                            ui_json = json.dumps({
                                "type": const.UI_FUNCTION_PREFIX,
                                "function": name,
                                **kwargs
                            })
                            # Convert to single quotes format as requested
                            ui_json_single_quotes = ui_json.replace('"', "'")
                            logger.debug(f"UI function JSON: {ui_json_single_quotes}")
                            return ui_json_single_quotes

                        # Execute regular function
                        if name not in context.methods_dict:
                            return f"Function '{name}' not found"

                        # Add required parameters and execute
                        kwargs.update({
                            'technical_id': context.technical_id,
                            'entity': context.entity
                        })

                        method = context.methods_dict[name]
                        if asyncio.iscoroutinefunction(method):
                            result = await method(context.cls_instance, **kwargs)
                        else:
                            result = method(context.cls_instance, **kwargs)

                        return str(result)

                    except Exception as e:
                        logger.exception(f"Error executing tool {name}: {e}")
                        return f"Error executing {name}: {str(e)}"

                return tool_function

            # Enhanced description for UI functions
            description = function_def.get("description", f"Execute {tool_name}")
            if tool_name.startswith(const.UI_FUNCTION_PREFIX):
                description = f"{description} CRITICAL: This is a UI function. Return ONLY the raw JSON output from this function call. Do not add any explanatory text."

            # Create FunctionTool using SDK patterns
            function_tool = FunctionTool(
                name=tool_name,
                description=description,
                params_json_schema=function_def.get("parameters", {}),
                on_invoke_tool=create_tool_function(tool_name)
            )

            function_tools.append(function_tool)
            logger.debug(f"Created function tool: {tool_name}")

        logger.info(f"Created {len(function_tools)} function tools")
        return function_tools

    def _sanitize_schema_for_openai(self, schema: dict) -> dict:
        """
        Sanitize JSON schema to be compatible with OpenAI's structured outputs.
        OpenAI has restrictions on certain JSON schema features.
        """
        def clean_schema_recursive(obj):
            if isinstance(obj, dict):
                cleaned = {}
                for key, value in obj.items():
                    # Remove unsupported features
                    if key in ['default', 'oneOf', 'anyOf', 'allOf', 'not', 'if', 'then', 'else']:
                        logger.debug(f"Removing unsupported schema feature: {key}")
                        continue

                    # Handle specific cases
                    if key == 'type' and isinstance(value, list):
                        # Convert type arrays to single type (take first)
                        cleaned[key] = value[0] if value else 'string'
                    elif key == 'additionalProperties':
                        # OpenAI requires explicit false for additionalProperties
                        cleaned[key] = False
                    else:
                        cleaned[key] = clean_schema_recursive(value)
                return cleaned
            elif isinstance(obj, list):
                return [clean_schema_recursive(item) for item in obj]
            else:
                return obj

        sanitized = clean_schema_recursive(schema)

        # Ensure required top-level properties
        if 'type' not in sanitized:
            sanitized['type'] = 'object'
        if 'additionalProperties' not in sanitized:
            sanitized['additionalProperties'] = False

        return sanitized

    def _create_openai_response_format(self, schema: dict) -> dict:
        """
        Create proper OpenAI response_format structure for structured outputs.
        OpenAI expects: {"type": "json_schema", "json_schema": {"name": "...", "schema": {...}}}
        """
        try:
            # Sanitize schema for OpenAI compatibility
            sanitized_schema = self._sanitize_schema_for_openai(schema)

            # Create proper OpenAI response_format structure
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": sanitized_schema.get('title', 'response'),
                    "schema": sanitized_schema,
                    "strict": True  # Enable strict mode for better validation
                }
            }

            logger.debug(f"Created OpenAI response_format: {response_format}")
            return response_format

        except Exception as e:
            logger.warning(f"Failed to create OpenAI response_format: {e}")
            # Fallback to simple JSON mode
            return {"type": "json_object"}

    def _create_agent(self, tools: List[FunctionTool], model: Any,
                     instructions: str, tool_choice: str = "auto",
                     response_format: Optional[Dict[str, Any]] = None,
                     original_tools: Optional[List[Dict[str, Any]]] = None) -> Agent:
        """
        Create an OpenAI Agents SDK Agent following modern best practices.
        Supports response_format for structured outputs using proper OpenAI format.
        """
        try:
            # Extract model name
            model_name = getattr(model, 'model_name', 'gpt-4o-mini')

            # Identify UI function names for stop_at_tool_names from original tools
            ui_function_names = []
            if original_tools:
                for tool in original_tools:
                    if tool.get("type") == "function":
                        func_name = tool.get("function", {}).get("name", "")
                        if func_name.startswith(const.UI_FUNCTION_PREFIX):
                            ui_function_names.append(func_name)
            else:
                # Fallback: extract from FunctionTool objects
                for tool in tools or []:
                    if hasattr(tool, 'name') and tool.name.startswith(const.UI_FUNCTION_PREFIX):
                        ui_function_names.append(tool.name)

            # Create model settings with tool_use_behavior for UI functions
            model_settings_kwargs = {
                'tool_choice': tool_choice,
                'temperature': getattr(model, 'temperature', 0.7),
                'max_tokens': getattr(model, 'max_tokens', None),
                'top_p': getattr(model, 'top_p', None)
            }

            # Add tool_use_behavior to stop execution when UI functions are called
            if ui_function_names:
                model_settings_kwargs['tool_use_behavior'] = {
                    "stop_at_tool_names": ui_function_names
                }
                logger.debug(f"Configured stop_at_tool_names for UI functions: {ui_function_names}")

            model_settings = ModelSettings(**model_settings_kwargs)

            # Handle response_format for structured outputs
            agent_kwargs = {
                'name': "Workflow Assistant",
                'instructions': instructions,
                'model': model_name,
                'model_settings': model_settings
            }

            # Add response format support
            if response_format and response_format.get("schema"):
                # Create proper OpenAI response_format instead of using output_type
                openai_response_format = self._create_openai_response_format(response_format["schema"])

                # Update model settings with response format
                model_settings.response_format = openai_response_format
                agent_kwargs['model_settings'] = model_settings

                # Add tools even with response format (OpenAI supports both)
                agent_kwargs['tools'] = tools

                logger.info(f"Using structured output with OpenAI response_format: {openai_response_format['type']}")
            else:
                # Normal mode with tools
                agent_kwargs['tools'] = tools

            agent = Agent(**agent_kwargs)
            logger.info(f"Created OpenAI Agent with {len(tools) if tools else 0} tools")
            return agent

        except Exception as e:
            logger.exception(f"Error creating OpenAI Agent: {e}")
            raise







    def adapt_messages(self, messages: List[AIMessage]) -> List[Dict[str, str]]:
        """
        Convert AIMessage objects to standard message format.
        Simplified version following SDK best practices.
        """
        adapted_messages = []
        for message in messages:
            if isinstance(message, AIMessage) and message.content:
                # Convert content to string
                if isinstance(message.content, list):
                    text_content = " ".join(str(item) for item in message.content)
                else:
                    text_content = str(message.content)

                adapted_messages.append({
                    "role": message.role or 'user',
                    "content": text_content
                })
        return adapted_messages





    def _extract_ui_function_result(self, response: str) -> Optional[str]:
        """
        Extract UI function JSON from agent response.
        Enhanced to handle cases where JSON is embedded in explanatory text.

        Args:
            response: Agent response that may contain UI function result

        Returns:
            UI function JSON if found, None otherwise
        """
        import re

        # Look for UI function JSON patterns - more comprehensive search
        patterns = [
            # Direct JSON patterns
            r'(\{[^{}]*"type":\s*"ui_function"[^{}]*\})',  # Simple JSON with ui_function type
            r'(\{[^{}]*"function":\s*"ui_function_[^"]*"[^{}]*\})',  # JSON with ui_function_ in function name

            # JSON with nested content
            r'(\{.*?"type":\s*"ui_function".*?\})',  # Complex JSON with ui_function type
            r'(\{.*?"function":\s*"ui_function_.*?\})',  # Complex JSON with ui_function_ in function name

            # JSON that might be quoted or escaped
            r'"(\{[^"]*"type":\s*"ui_function"[^"]*\})"',  # Quoted JSON
            r"'(\{[^']*'type':\s*'ui_function'[^']*\})'",  # Single-quoted JSON
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
                        logger.debug(f"Extracted UI function result using pattern: {pattern}")
                        logger.debug(f"Extracted JSON: {ui_json}")
                        return ui_json
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON decode error for '{ui_json}': {e}")
                    continue

        # If no patterns match, try to find any JSON-like structure and check if it's a UI function
        json_pattern = r'\{[^{}]*\}'
        json_matches = re.findall(json_pattern, response)
        for json_match in json_matches:
            try:
                parsed = json.loads(json_match)
                if (isinstance(parsed, dict) and
                    (parsed.get("type") == const.UI_FUNCTION_PREFIX or
                     str(parsed.get("function", "")).startswith(const.UI_FUNCTION_PREFIX))):
                    logger.debug(f"Found UI function JSON in fallback search: {json_match}")
                    return json_match
            except json.JSONDecodeError:
                continue

        return None

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
            if not JSONSCHEMA_AVAILABLE:
                logger.warning("jsonschema not available, skipping validation")
                return content, None

            parsed = json.loads(content)
            jsonschema.validate(instance=parsed, schema=schema)
            return content, None
        except (json.JSONDecodeError, ValidationError) as e:
            error = str(e)
            error = (error[:100] + '...') if len(error) > 100 else error
            msg = f"Validation failed on attempt {attempt}/{max_retries}: {error}. Please return correct JSON."
            if attempt > 2:
                msg = f"{msg} If the task is too complex, simplify but ensure valid JSON."
            return None, msg

    async def _validate_and_retry_schema(self, response: str, schema: dict,
                                        tools: List[FunctionTool], model: Any,
                                        instructions: str, tool_choice: str,
                                        messages: List[Dict[str, str]]) -> str:
        """
        Validate response against schema and retry if needed.
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
                    # Create correction message
                    correction_messages = messages + [{
                        "role": "user",
                        "content": f"The previous response had validation errors: {error}"
                    }]

                    # Create new agent for retry
                    retry_agent = self._create_agent(tools, model, instructions, tool_choice,
                                                   {"schema": schema})

                    # Create run configuration
                    run_config = RunConfig(
                        workflow_name="OpenAI_SDK_Agent_Retry",
                        trace_id=f"retry_{attempt}"
                    )

                    # Run retry
                    retry_result = await Runner.run(
                        starting_agent=retry_agent,
                        input=correction_messages,
                        session=None,
                        run_config=run_config,
                        max_turns=1
                    )

                    response = str(retry_result.final_output)

                except Exception as e:
                    logger.exception(f"Error during validation retry {attempt}: {e}")
                    break

        # If all retries failed, return the last response with a warning
        logger.error(f"Schema validation failed after {self.max_calls} attempts. Returning last response.")
        return response

    def _is_ui_function_json(self, response: str) -> bool:
        """Check if the response is a direct UI function JSON (matching ADK agent logic)."""
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

    async def run_agent(self, methods_dict: Dict[str, Any], technical_id: str,
                       cls_instance: Any, entity: Any, tools: List[Dict[str, Any]],
                       model: Any, messages: List[AIMessage], tool_choice: str = "auto",
                       response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Main method to run the OpenAI Agents SDK agent.

        Args:
            methods_dict: Dictionary of available methods/tools
            technical_id: Technical identifier for the session
            cls_instance: Class instance for method calls
            entity: Entity object for context
            tools: List of tool definitions
            model: Model configuration
            messages: List of AIMessage objects
            tool_choice: Tool choice strategy ("auto", "required", "none", or specific tool name)
            response_format: Optional response format with schema for validation

        Returns:
            Agent response as string
        """
        try:
            # Create context for dependency injection
            context = OpenAiSdkAgentContext(
                methods_dict=methods_dict,
                technical_id=technical_id,
                cls_instance=cls_instance,
                entity=entity
            )

            # Convert messages to standard format
            adapted_messages = self.adapt_messages(messages)

            # Create function tools from JSON definitions
            function_tools = self._create_function_tools(tools, context)

            # Create agent with enhanced instructions for UI functions
            has_ui_functions = any(tool.get("function", {}).get("name", "").startswith(const.UI_FUNCTION_PREFIX)
                                 for tool in (tools or []) if tool and tool.get("type") == "function")

            # Simplified instructions since tool_use_behavior handles UI function stopping
            instructions = "You are a helpful assistant that can use tools to complete tasks."

            agent = self._create_agent(function_tools, model, instructions, tool_choice, response_format, tools)

            # Always use full message history - no sessions needed since we have all context in messages
            agent_input = adapted_messages if adapted_messages else [{"role": "user", "content": "Please help me."}]

            logger.info(f"Running agent with {len(function_tools)} tools and {len(agent_input)} messages")
            logger.debug(f"Message history: {[msg.get('role', 'unknown') for msg in agent_input]}")

            # Create run configuration
            run_config = RunConfig(
                workflow_name="OpenAI_SDK_Agent",
                trace_id=f"trace_{technical_id}"
            )

            # Run the agent with full message history (no session needed)
            result = await Runner.run(
                starting_agent=agent,
                input=agent_input,
                session=None,  # No session needed - all context is in messages
                run_config=run_config,
                max_turns=self.max_calls
            )

            response = str(result.final_output)
            logger.info(f"Agent completed successfully")
            logger.debug(f"Raw agent response: {response}")

            # Check if execution was stopped due to UI function tool call
            if hasattr(result, 'tool_calls') and result.tool_calls:
                # Check if any tool call was a UI function
                for call in result.tool_calls:
                    if hasattr(call, 'function') and call.function.name.startswith(const.UI_FUNCTION_PREFIX):
                        logger.debug(f"Execution stopped at UI function: {call.function.name}")

                        # Parse arguments if available
                        args = {}
                        if hasattr(call.function, 'arguments') and call.function.arguments:
                            try:
                                args = json.loads(call.function.arguments)
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse UI function arguments: {call.function.arguments}")

                        # Return UI function JSON directly (single quotes as requested)
                        if isinstance(args, dict):
                            ui_json = json.dumps({"type": const.UI_FUNCTION_PREFIX, "function": call.function.name, **args})
                        else:
                            ui_json = json.dumps({"type": const.UI_FUNCTION_PREFIX, "function": call.function.name})

                        # Convert to single quotes format
                        ui_json_single_quotes = ui_json.replace('"', "'")
                        logger.debug(f"UI function JSON: {ui_json_single_quotes}")
                        return ui_json_single_quotes

            # Check if the response itself contains UI function JSON
            if self._is_ui_function_json(response.strip()):
                logger.debug("Response is direct UI function JSON")
                return response.strip()

            # Handle schema validation for structured outputs
            if response_format and response_format.get("schema"):
                validated_response = await self._validate_and_retry_schema(
                    response, response_format["schema"], function_tools, model,
                    instructions, tool_choice, adapted_messages
                )
                return validated_response

            return response

        except MaxTurnsExceeded as e:
            logger.warning(f"Agent exceeded max turns ({self.max_calls}): {e}")
            return f"Agent exceeded maximum iterations ({self.max_calls}). Please try a simpler request."

        except ModelBehaviorError as e:
            logger.error(f"Model behavior error: {e}")
            return f"Model produced unexpected output: {str(e)}"

        except AgentsException as e:
            logger.error(f"Agents SDK error: {e}")
            return f"Agent execution error: {str(e)}"

        except Exception as e:
            logger.exception(f"Unexpected error in OpenAI SDK agent execution: {e}")
            return f"Unexpected error occurred: {str(e)}"

        finally:
            # No session management needed - all context is in messages
            logger.debug("Run completed - no session cleanup needed")



    async def cleanup(self):
        """
        Clean up resources. OpenAI Agents SDK handles most cleanup automatically.
        """
        try:
            logger.debug("Cleanup completed")
        except Exception as e:
            logger.exception(f"Error during cleanup: {e}")
