"""
Main OpenAI SDK Agent implementation.

Orchestrates all adapter components to provide a clean, modular implementation
of the OpenAI Agents SDK integration following clean architecture principles.
"""

import logging
from typing import Dict, Any, List, Optional

try:
    from agents import Agent, Runner, ModelSettings, RunConfig, FunctionTool
    from agents import AgentsException, MaxTurnsExceeded, ModelBehaviorError
    from agents.tool_context import ToolContext
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    Agent = Any
    Runner = Any
    ModelSettings = Any
    RunConfig = Any
    FunctionTool = Any
    ToolContext = Any
    AgentsException = Exception
    MaxTurnsExceeded = Exception
    ModelBehaviorError = Exception
    AGENTS_SDK_AVAILABLE = False

from common.config.config import config
from common.config import const
from entity.model import AIMessage

from .context import OpenAiSdkAgentContext
from .adapters.message_adapter import MessageAdapter
from .adapters.tool_adapter import ToolAdapter
from .adapters.ui_function_handler import UiFunctionHandler
from .adapters.schema_adapter import SchemaAdapter

logger = logging.getLogger(__name__)


class OpenAiSdkAgent:
    """
    OpenAI Agents SDK-based AI Agent following clean architecture principles.
    
    This implementation uses dependency injection and separation of concerns
    to provide a maintainable, testable, and extensible agent system.
    
    Components:
    - MessageAdapter: Handles message format conversion
    - ToolAdapter: Manages tool creation and execution
    - UiFunctionHandler: Handles UI function special behavior
    - SchemaAdapter: Manages JSON schema operations
    """

    def __init__(self, max_calls: int = config.MAX_AI_AGENT_ITERATIONS):
        """
        Initialize the OpenAI SDK Agent with all required adapters.

        Args:
            max_calls: Maximum number of agent iterations (max_turns in SDK)
        """
        self.max_calls = max_calls
        
        # Initialize adapters with dependency injection
        self.ui_function_handler = UiFunctionHandler()
        self.message_adapter = MessageAdapter()
        self.tool_adapter = ToolAdapter(self.ui_function_handler)
        self.schema_adapter = SchemaAdapter()
        
        logger.info(f"Initialized OpenAI SDK Agent with max_calls: {max_calls}")

    def adapt_messages(self, messages: List[AIMessage]) -> List[Dict[str, str]]:
        """
        Adapt AIMessage objects to standard message format.

        This method provides backward compatibility with the deprecated implementation.
        """
        return self.message_adapter.adapt_messages(messages)

    def _is_ui_function_json(self, response: str) -> bool:
        """
        Check if the response is a direct UI function JSON.

        This method provides backward compatibility with the deprecated implementation.
        """
        return self.ui_function_handler.is_ui_function_json(response)

    async def run_agent(self, methods_dict: Dict[str, Any], technical_id: str,
                       cls_instance: Any, entity: Any, tools: List[Dict[str, Any]],
                       model: Any, messages: List[AIMessage], tool_choice: str = "auto",
                       response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Main method to run the OpenAI Agents SDK agent.
        
        Clean orchestration of all adapter components to execute the agent
        with proper error handling and result processing.

        Args:
            methods_dict: Dictionary of available methods/tools
            technical_id: Technical identifier for the session
            cls_instance: Class instance for method calls
            entity: Entity object for context
            tools: List of tool definitions in JSON format
            model: Model configuration
            messages: List of AIMessage objects
            tool_choice: Tool choice strategy ("auto", "required", "none", or specific tool name)
            response_format: Optional response format with schema for validation

        Returns:
            Agent response as string
        """
        if not AGENTS_SDK_AVAILABLE:
            logger.warning("OpenAI Agents SDK not available, returning mock response")
            return "OpenAI Agents SDK not installed. Please install the agents package to use OpenAI agent functionality."

        try:
            # Setup execution context
            context = OpenAiSdkAgentContext(
                methods_dict=methods_dict,
                technical_id=technical_id,
                cls_instance=cls_instance,
                entity=entity
            )
            
            # Prepare agent components using adapters
            adapted_messages = self.message_adapter.adapt_messages(messages)
            function_tools = self.tool_adapter.create_function_tools(tools, context)
            
            # Create and configure agent
            agent = self._create_configured_agent(
                function_tools, model, tool_choice, response_format, tools
            )
            
            # Execute agent with proper configuration
            result = await self._execute_agent(
                agent, adapted_messages, technical_id
            )
            
            # Process and return result using adapters
            return await self._process_agent_result(
                result, response_format, function_tools, model, tool_choice, adapted_messages
            )

        except (MaxTurnsExceeded, ModelBehaviorError, AgentsException) as e:
            return self._handle_agent_exception(e)
        except Exception as e:
            logger.exception(f"Unexpected error in OpenAI SDK agent execution: {e}")
            return f"Unexpected error occurred: {str(e)}"
        finally:
            logger.debug("Run completed - no session cleanup needed")

    def _create_configured_agent(self, function_tools: List[Any], model: Any,
                                tool_choice: str, response_format: Optional[Dict[str, Any]],
                                original_tools: List[Dict[str, Any]]) -> Any:
        """
        Create agent with proper configuration using adapters.
        
        Args:
            function_tools: List of FunctionTool objects
            model: Model configuration
            tool_choice: Tool choice strategy
            response_format: Optional response format
            original_tools: Original JSON tool definitions
            
        Returns:
            Configured Agent object
        """
        if not AGENTS_SDK_AVAILABLE:
            logger.warning("OpenAI Agents SDK not available, returning mock agent")
            class MockAgent:
                def __init__(self, model_name, tools):
                    self.model = model_name
                    self.tools = tools
                    self.name = "mock_openai_agent"
            model_config = self._extract_model_config(model)
            return MockAgent(model_config['name'], function_tools)

        # Extract model configuration
        model_config = self._extract_model_config(model)
        
        # Configure UI function behavior using UI function handler
        ui_function_names = self.ui_function_handler.extract_ui_function_names(original_tools)
        
        # Build model settings with proper configuration
        model_settings = self._build_model_settings(
            model_config, tool_choice, ui_function_names, response_format
        )
        
        # Create agent with clean configuration
        agent_config = {
            'name': "Workflow Assistant",
            'instructions': "You are a helpful assistant that can use tools to complete tasks.",
            'model': model_config['name'],
            'model_settings': model_settings,
            'tools': function_tools
        }
        
        return Agent(**agent_config)

    def _extract_model_config(self, model: Any) -> Dict[str, Any]:
        """Extract model configuration parameters."""
        return {
            'name': getattr(model, 'model_name', 'gpt-4o-mini'),
            'temperature': getattr(model, 'temperature', 0.7),
            'max_tokens': getattr(model, 'max_tokens', None),
            'top_p': getattr(model, 'top_p', None)
        }

    def _build_model_settings(self, model_config: Dict[str, Any], tool_choice: str,
                             ui_function_names: List[str],
                             response_format: Optional[Dict[str, Any]]) -> Any:
        """Build ModelSettings with proper configuration using schema adapter."""
        if not AGENTS_SDK_AVAILABLE:
            logger.warning("OpenAI Agents SDK not available, returning mock model settings")
            class MockModelSettings:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            return MockModelSettings(
                tool_choice=tool_choice,
                temperature=model_config['temperature'],
                max_tokens=model_config['max_tokens'],
                top_p=model_config['top_p']
            )

        model_settings_kwargs = {
            'tool_choice': tool_choice,
            'temperature': model_config['temperature'],
            'max_tokens': model_config['max_tokens'],
            'top_p': model_config['top_p']
        }

        # Configure tool use behavior for UI functions
        if ui_function_names:
            model_settings_kwargs['tool_use_behavior'] = {
                "stop_at_tool_names": ui_function_names
            }

        model_settings = ModelSettings(**model_settings_kwargs)

        # Add response format if specified using schema adapter
        if response_format and response_format.get("schema"):
            openai_response_format = self.schema_adapter.create_response_format(
                response_format["schema"]
            )
            model_settings.response_format = openai_response_format
            logger.info(f"Using structured output with OpenAI response_format: {openai_response_format['type']}")

        return model_settings

    async def _execute_agent(self, agent: Any, adapted_messages: List[Dict[str, str]],
                            technical_id: str) -> Any:
        """Execute the agent with proper configuration."""
        if not AGENTS_SDK_AVAILABLE:
            logger.warning("OpenAI Agents SDK not available, returning mock response")
            return "Mock agent execution - OpenAI Agents SDK not available"

        # Ensure we have valid input
        agent_input = adapted_messages if adapted_messages else [
            self.message_adapter.create_default_message()
        ]

        logger.info(f"Running agent with {len(agent.tools) if agent.tools else 0} tools "
                   f"and {len(agent_input)} messages")
        logger.debug(f"Message history: {[msg.get('role', 'unknown') for msg in agent_input]}")

        # Create run configuration
        run_config = RunConfig(
            workflow_name="OpenAI_SDK_Agent",
            trace_id=f"trace_{technical_id}"
        )

        # Execute agent (no session needed - all context is in messages)
        return await Runner.run(
            starting_agent=agent,
            input=agent_input,
            session=None,
            run_config=run_config,
            max_turns=self.max_calls
        )

    async def _process_agent_result(self, result: Any, response_format: Optional[Dict[str, Any]],
                                   function_tools: List[Any], model: Any,
                                   tool_choice: str, adapted_messages: List[Dict[str, str]]) -> str:
        """Process agent execution result using adapters."""
        response = str(result.final_output)
        logger.info("Agent completed successfully")
        logger.debug(f"Raw agent response: {response}")

        # Check for UI function tool calls using UI function handler
        ui_result = self.ui_function_handler.extract_ui_function_from_result(result)
        if ui_result:
            return ui_result

        # Check if response itself is UI function JSON
        if self.ui_function_handler.is_ui_function_json(response.strip()):
            logger.debug("Response is direct UI function JSON")
            return response.strip()

        # Handle schema validation for structured outputs using schema adapter
        if response_format and response_format.get("schema"):
            return await self._validate_and_retry_schema(
                response, response_format["schema"], function_tools, model,
                tool_choice, adapted_messages
            )

        return response

    async def _validate_and_retry_schema(self, response: str, schema: Dict[str, Any],
                                        function_tools: List[Any], model: Any,
                                        tool_choice: str, adapted_messages: List[Dict[str, str]]) -> str:
        """Validate response against schema and retry if needed using schema adapter."""
        for attempt in range(1, self.max_calls + 1):
            is_valid, error = self.schema_adapter.validate_schema(response, schema)
            if is_valid:
                return response

            # If validation failed, retry with correction
            logger.warning(f"Schema validation failed on attempt {attempt}: {error}")

            if attempt < self.max_calls:
                try:
                    # Create correction message
                    correction_messages = adapted_messages + [{
                        "role": "user",
                        "content": f"The previous response had validation errors: {error}"
                    }]

                    # Create new agent for retry
                    retry_agent = self._create_configured_agent(
                        function_tools, model, tool_choice, {"schema": schema}, []
                    )

                    # Execute retry
                    retry_result = await self._execute_agent(retry_agent, correction_messages, "retry")
                    response = str(retry_result.final_output)

                except Exception as e:
                    logger.exception(f"Error during validation retry {attempt}: {e}")
                    break

        # If all retries failed, return the last response with a warning
        logger.error(f"Schema validation failed after {self.max_calls} attempts. Returning last response.")
        return response

    def _handle_agent_exception(self, e: Exception) -> str:
        """Handle specific agent exceptions with appropriate error messages."""
        if isinstance(e, MaxTurnsExceeded):
            logger.warning(f"Agent exceeded max turns ({self.max_calls}): {e}")
            return f"Agent exceeded maximum iterations ({self.max_calls}). Please try a simpler request."
        elif isinstance(e, ModelBehaviorError):
            logger.error(f"Model behavior error: {e}")
            return f"Model produced unexpected output: {str(e)}"
        elif isinstance(e, AgentsException):
            logger.error(f"Agents SDK error: {e}")
            return f"Agent execution error: {str(e)}"
        else:
            logger.exception(f"Unexpected agent exception: {e}")
            return f"Agent error: {str(e)}"
