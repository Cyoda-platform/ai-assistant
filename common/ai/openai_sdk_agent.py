import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Type
import os

import jsonschema
from jsonschema import ValidationError
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

                        # Handle UI functions - return clean JSON directly like ADK agent
                        if name.startswith(const.UI_FUNCTION_PREFIX):
                            logger.debug(f"Handling UI function: {name}")
                            ui_json = json.dumps({
                                "type": const.UI_FUNCTION_PREFIX,
                                "function": name,
                                **kwargs
                            })
                            return ui_json

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

    def _create_output_type_from_schema(self, schema: dict) -> Type[BaseModel]:
        """
        Create a Pydantic model from JSON schema for structured outputs.
        Following OpenAI Agents SDK best practices for output_type.
        """
        try:
            from pydantic import create_model

            # Extract properties and create Pydantic fields
            properties = schema.get('properties', {})
            required_fields = schema.get('required', [])

            # Build field definitions for Pydantic
            field_definitions = {}
            for field_name, field_def in properties.items():
                field_type = str  # Default to string

                # Map JSON schema types to Python types
                json_type = field_def.get('type', 'string')
                if json_type == 'integer':
                    field_type = int
                elif json_type == 'number':
                    field_type = float
                elif json_type == 'boolean':
                    field_type = bool
                elif json_type == 'array':
                    field_type = List[str]  # Simplified array handling

                # Handle required vs optional fields
                if field_name in required_fields:
                    field_definitions[field_name] = (field_type, ...)
                else:
                    field_definitions[field_name] = (Optional[field_type], None)

            # Create dynamic Pydantic model
            model_name = schema.get('title', 'ResponseModel')
            return create_model(model_name, **field_definitions)

        except Exception as e:
            logger.warning(f"Failed to create Pydantic model from schema: {e}")
            # Fallback to a simple string response
            return str

    def _create_agent(self, tools: List[FunctionTool], model: Any,
                     instructions: str, tool_choice: str = "auto",
                     response_format: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create an OpenAI Agents SDK Agent following modern best practices.
        Supports response_format for structured outputs.
        """
        try:
            # Extract model name
            model_name = getattr(model, 'model_name', 'gpt-4o-mini')

            # Create model settings following SDK best practices
            model_settings = ModelSettings(
                tool_choice=tool_choice,
                temperature=getattr(model, 'temperature', 0.7),
                max_tokens=getattr(model, 'max_tokens', None),
                top_p=getattr(model, 'top_p', None)
            )

            # Handle response_format for structured outputs
            agent_kwargs = {
                'name': "Workflow Assistant",
                'instructions': instructions,
                'model': model_name,
                'model_settings': model_settings
            }

            # Add response format support
            if response_format and response_format.get("schema"):
                # Convert JSON schema to Pydantic model for output_type
                output_type = self._create_output_type_from_schema(response_format["schema"])
                agent_kwargs['output_type'] = output_type
                logger.info("Using structured output with response schema")
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

            if has_ui_functions:
                instructions = """You are a helpful assistant that can use tools to complete tasks.

CRITICAL INSTRUCTION FOR UI FUNCTIONS:
When you call a function that starts with 'ui_function_', you MUST return ONLY the raw JSON output from that function call.

ABSOLUTELY NO explanatory text, confirmation messages, greetings, or additional content of any kind.
ABSOLUTELY NO phrases like "Here's the information you requested" or "Let me know if you need anything else".
RETURN ONLY THE EXACT JSON STRING FROM THE FUNCTION CALL.

Example of CORRECT response for UI function:
{"type": "ui_function", "function": "ui_function_list_all_technical_users", "method": "GET", "path": "/api/clients", "response_format": "text"}

Example of INCORRECT response for UI function:
Here's the M2M user information you requested: {"type": "ui_function", ...}

For regular functions, you may provide explanatory text as normal."""
            else:
                instructions = "You are a helpful assistant that can use tools to complete tasks."

            agent = self._create_agent(function_tools, model, instructions, tool_choice, response_format)

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

            # For UI functions, prioritize JSON extraction over everything else
            if has_ui_functions:
                # First check if the response itself is a UI function JSON
                if self._is_ui_function_json(response.strip()):
                    logger.debug("Response is direct UI function JSON")
                    return response.strip()

                # Then try to extract UI function result from within the response
                ui_function_result = self._extract_ui_function_result(response)
                if ui_function_result:
                    logger.debug(f"Extracted UI function result: {ui_function_result}")
                    return ui_function_result

                # If we have UI functions but couldn't extract JSON, log warning
                logger.warning(f"UI functions available but no UI function JSON found in response: {response}")
            else:
                # For non-UI function responses, still check for UI function results
                ui_function_result = self._extract_ui_function_result(response)
                if ui_function_result:
                    logger.debug(f"Extracted UI function result: {ui_function_result}")
                    return ui_function_result

            # When using output_type, SDK handles structured output validation automatically
            # No manual schema validation needed
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
