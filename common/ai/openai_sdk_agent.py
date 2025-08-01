import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
import os

import jsonschema
from jsonschema import ValidationError

# OpenAI Agents SDK imports
from agents import (
    Agent, Runner, function_tool, FunctionTool, ModelSettings,
    SQLiteSession, Session, AgentsException, MaxTurnsExceeded,
    ModelBehaviorError, RunConfig
)
from agents.tool_context import ToolContext

from common.config import const
from common.config.config import config
from entity.model import AIMessage

logger = logging.getLogger(__name__)


class OpenAiSdkAgentContext:
    """Context object for dependency injection in OpenAI Agents SDK"""

    def __init__(self, methods_dict: Dict[str, Any], technical_id: str,
                 cls_instance: Any, entity: Any, ui_function_handler: Any = None):
        self.methods_dict = methods_dict or {}
        self.technical_id = technical_id
        self.cls_instance = cls_instance
        self.entity = entity
        self.ui_function_handler = ui_function_handler


class OpenAiSdkAgent:
    """
    OpenAI Agents SDK-based AI Agent using the modern OpenAI Agents framework.
    Provides advanced features like proper agent orchestration, handoffs,
    guardrails, sessions, and comprehensive tool management.
    """

    def __init__(self, max_calls=config.MAX_AI_AGENT_ITERATIONS):
        """
        Initialize the OpenAI SDK Agent.

        Args:
            max_calls: Maximum number of agent iterations (max_turns in SDK)
        """
        self.max_calls = max_calls
        self.session = None
        self._function_tools_cache = {}

    def _create_function_tools(self, tools: List[Dict[str, Any]],
                              context: OpenAiSdkAgentContext) -> List[FunctionTool]:
        """
        Convert JSON tool definitions to OpenAI Agents SDK FunctionTool objects.

        Args:
            tools: List of tool definitions in JSON format
            context: Agent context for dependency injection

        Returns:
            List of FunctionTool objects
        """
        function_tools = []

        for tool in tools or []:
            if tool.get("type") == "function":
                function_def = tool.get("function", {})
                tool_name = function_def.get("name")

                if not tool_name:
                    logger.warning(f"Tool missing name: {tool}")
                    continue

                # Create tool function
                def create_tool_function(name: str):
                    async def tool_function(ctx: ToolContext, args_json: str) -> str:
                        """Dynamically created tool function"""
                        try:
                            # Parse arguments from JSON
                            try:
                                kwargs = json.loads(args_json)
                            except json.JSONDecodeError as e:
                                return f"Invalid JSON arguments: {e}"

                            # Check if this is a UI function that needs special handling
                            if name.startswith(const.UI_FUNCTION_PREFIX):
                                logger.debug(f"Handling UI function: {name}")
                                # For UI functions, return JSON with special instruction
                                ui_json = json.dumps({
                                    "type": const.UI_FUNCTION_PREFIX,
                                    "function": name,
                                    **kwargs
                                })
                                # Return with instruction to the LLM to return only this JSON
                                return f"UI_FUNCTION_RESULT:{ui_json}:END_UI_FUNCTION"

                            # Get the method from context
                            if name not in context.methods_dict:
                                available_methods = list(context.methods_dict.keys())
                                return f"Function '{name}' not found. Available: {available_methods}"

                            # Add required parameters
                            kwargs.update({
                                'technical_id': context.technical_id,
                                'entity': context.entity
                            })

                            # Execute the method
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

                # Enhance description for UI functions
                original_description = function_def.get("description", f"Execute {tool_name}")
                if tool_name.startswith(const.UI_FUNCTION_PREFIX):
                    enhanced_description = f"{original_description} CRITICAL: This is a UI function. You MUST return ONLY the raw JSON output from this function call. Do not add any explanatory text, confirmation messages, or additional content. Return the JSON exactly as provided by the function."
                else:
                    enhanced_description = original_description

                # Create FunctionTool
                function_tool = FunctionTool(
                    name=tool_name,
                    description=enhanced_description,
                    params_json_schema=function_def.get("parameters", {}),
                    on_invoke_tool=create_tool_function(tool_name)
                )

                function_tools.append(function_tool)
                logger.debug(f"Created function tool: {tool_name}")

        return function_tools

    def _create_agent(self, tools: List[FunctionTool], model: Any,
                     instructions: str, tool_choice: str = "auto") -> Agent:
        """
        Create an OpenAI Agents SDK Agent.

        Args:
            tools: List of FunctionTool objects
            model: Model configuration
            instructions: Agent instructions
            tool_choice: Tool choice strategy

        Returns:
            Agent instance
        """
        try:
            # Extract model name
            model_name = model.model_name if hasattr(model, 'model_name') else 'gpt-4.1-mini'

            # Create model settings
            model_settings = ModelSettings(
                model=model_name,
                tool_choice=tool_choice,
                temperature=getattr(model, 'temperature', 0.7),
                max_tokens=getattr(model, 'max_tokens', None),
                top_p=getattr(model, 'top_p', None)
            )

            # Create agent
            agent = Agent(
                name="Workflow Assistant",
                instructions=instructions,
                model=model_name,
                model_settings=model_settings,
                tools=tools
            )

            logger.info(f"Created OpenAI Agent with {len(tools)} tools")
            return agent

        except Exception as e:
            logger.exception(f"Error creating OpenAI Agent: {e}")
            raise

    def _convert_messages_to_input(self, messages: List[Dict[str, str]], use_session: bool = True) -> Union[str, List[Dict[str, str]]]:
        """
        Convert messages to input format for OpenAI Agents SDK.

        Args:
            messages: List of message dictionaries
            use_session: Whether session management is being used

        Returns:
            Input for the agent (string when using session, list when not using session)
        """
        if not messages:
            return "Please help me."

        if use_session:
            # When using session, only provide the latest user message as string
            # The session will handle conversation history automatically
            latest_message = messages[-1] if messages else {"content": "Please help me."}
            return latest_message.get("content", "Please help me.")
        else:
            # When not using session, provide full conversation history as list
            return messages

    async def _create_session(self, technical_id: str, messages: List[Dict[str, str]]) -> Session:
        """
        Create or get session for conversation management.

        Args:
            technical_id: Technical identifier for the session
            messages: List of message dictionaries (for future use)

        Returns:
            Session instance
        """
        try:
            if not self.session:
                self.session = SQLiteSession(session_id=f"session_{technical_id}")
                logger.debug(f"Created new session: session_{technical_id}")

            return self.session

        except Exception as e:
            logger.exception(f"Error creating session: {e}")
            raise

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

    def adapt_messages(self, messages: List[AIMessage]) -> List[Dict[str, str]]:
        """
        Convert AIMessage objects to standard message format.

        Args:
            messages: List of AIMessage objects

        Returns:
            List of message dictionaries
        """
        adapted_messages = []
        for message in messages:
            if isinstance(message, AIMessage):
                content = message.content
                if content:
                    # Convert to string content
                    text_content = " ".join(content) if isinstance(content, list) else content
                    adapted_messages.append({
                        "role": message.role or 'user',
                        "content": text_content
                    })
            else:
                logger.warning(f"Unexpected message type: {type(message)}")
        return adapted_messages

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



    def _extract_ui_function_result(self, response: str) -> Optional[str]:
        """
        Extract UI function JSON from agent response.

        Args:
            response: Agent response that may contain UI function result

        Returns:
            UI function JSON if found, None otherwise
        """
        import re

        # Look for UI function result patterns
        patterns = [
            r'UI_FUNCTION_RESULT:(.+?):END_UI_FUNCTION',  # Original pattern
            r'(.+?):END_UI_FUNCTION',  # New pattern for direct JSON
            r'(\{.*?"type":\s*"ui_function".*?\})'  # Fallback: JSON with ui_function type
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                ui_json = match.group(1).strip()
                try:
                    # Validate it's proper JSON and contains ui_function type
                    parsed = json.loads(ui_json)
                    if parsed.get("type") == "ui_function":
                        return ui_json
                except json.JSONDecodeError:
                    continue

        return None

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
                entity=entity,
                ui_function_handler=self._handle_ui_functions
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
When you call a function that starts with 'ui_function_', you MUST return ONLY the raw JSON output from that function call. Do not add any explanatory text, confirmation messages, or additional content. Return the JSON exactly as provided by the function, nothing more, nothing less.

For regular functions, you may provide explanatory text as normal."""
            else:
                instructions = "You are a helpful assistant that can use tools to complete tasks."

            agent = self._create_agent(function_tools, model, instructions, tool_choice)

            # Decide whether to use session or manual conversation management
            use_session = len(adapted_messages) <= 1

            if use_session:
                # For single messages, use session management
                session = await self._create_session(technical_id, adapted_messages)
                agent_input = self._convert_messages_to_input(adapted_messages, use_session=True)
            else:
                # For multiple messages, use manual conversation management
                session = None
                agent_input = self._convert_messages_to_input(adapted_messages, use_session=False)

            # Create run configuration
            run_config = RunConfig(
                workflow_name="OpenAI_SDK_Agent",
                trace_id=f"trace_{technical_id}"
            )

            # Run the agent
            logger.info(f"Running agent with {len(function_tools)} tools")
            result = await Runner.run(
                starting_agent=agent,
                input=agent_input,
                session=session,
                run_config=run_config,
                max_turns=self.max_calls
            )

            response = str(result.final_output)
            logger.info(f"Agent completed successfully")

            # Check if this is a UI function result that should return only JSON
            ui_function_result = self._extract_ui_function_result(response)
            if ui_function_result:
                logger.debug(f"Extracted UI function result: {ui_function_result}")
                return ui_function_result

            # Handle schema validation if required
            if response_format and response_format.get("schema"):
                response = await self._handle_schema_validation(
                    response, response_format["schema"], agent, session, run_config
                )

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

    async def _handle_schema_validation(self, response: str, schema: dict,
                                       agent: Agent, session: Session,
                                       run_config: RunConfig) -> str:
        """
        Handle schema validation with retries.

        Args:
            response: Initial response to validate
            schema: JSON schema for validation
            agent: Agent instance for retries
            session: Session for conversation continuity
            run_config: Run configuration

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
                    correction_input = f"The previous response had validation errors: {error}"
                    # For schema validation retries, always use session if available
                    # since we want to maintain conversation context
                    result = await Runner.run(
                        starting_agent=agent,
                        input=correction_input,
                        session=session,
                        run_config=run_config
                    )
                    response = str(result.final_output)
                except Exception as e:
                    logger.exception(f"Error during validation retry {attempt}: {e}")
                    break

        # If all retries failed
        raise Exception(f"Schema validation failed after {self.max_calls} attempts. Last response: {response}")

    async def cleanup(self):
        """
        Clean up resources.

        Note: OpenAI Agents SDK handles most cleanup automatically,
        but we can clear our session cache.
        """
        try:
            if self.session:
                # Sessions are typically managed automatically
                self.session = None
                logger.debug("Cleared session cache")

            # Clear function tools cache
            self._function_tools_cache.clear()
            logger.debug("Cleared function tools cache")

        except Exception as e:
            logger.exception(f"Error during cleanup: {e}")

    def __del__(self):
        """
        Destructor to ensure cleanup.

        Note: OpenAI Agents SDK manages resources automatically,
        so minimal cleanup is needed.
        """
        try:
            # Clear caches
            if hasattr(self, '_function_tools_cache'):
                self._function_tools_cache.clear()
        except:
            pass
