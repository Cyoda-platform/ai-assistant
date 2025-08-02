"""
Main Google ADK Agent implementation.

Orchestrates all adapter components to provide a clean, modular implementation
of the Google ADK integration following clean architecture principles.
"""

import logging
from typing import Dict, Any, List, Optional

try:
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.models.lite_llm import LiteLlm
    ADK_AVAILABLE = True
except ImportError:
    Agent = Any
    Runner = Any
    InMemorySessionService = Any
    LiteLlm = Any
    ADK_AVAILABLE = False

from common.config.config import config
from entity.model import AIMessage

from .context import AdkAgentContext
from .adapters.message_adapter import AdkMessageAdapter
from .adapters.tool_adapter import AdkToolAdapter
from .adapters.ui_function_handler import AdkUiFunctionHandler
from .adapters.schema_adapter import AdkSchemaAdapter

logger = logging.getLogger(__name__)


class AdkAgent:
    """
    Google ADK-based AI Agent following clean architecture principles.
    
    This implementation uses dependency injection and separation of concerns
    to provide a maintainable, testable, and extensible agent system.
    
    Components:
    - AdkMessageAdapter: Handles message format conversion
    - AdkToolAdapter: Manages tool creation and execution
    - AdkUiFunctionHandler: Handles UI function special behavior
    - AdkSchemaAdapter: Manages JSON schema operations
    """

    def __init__(self, max_calls: int = config.MAX_AI_AGENT_ITERATIONS):
        """
        Initialize the Google ADK Agent with all required adapters.

        Args:
            max_calls: Maximum number of agent iterations
        """
        self.max_calls = max_calls
        
        # Initialize adapters with dependency injection
        self.ui_function_handler = AdkUiFunctionHandler()
        self.message_adapter = AdkMessageAdapter()
        self.tool_adapter = AdkToolAdapter(self.ui_function_handler)
        self.schema_adapter = AdkSchemaAdapter()
        
        logger.info(f"Initialized Google ADK Agent with max_calls: {max_calls}")

    async def run_agent(self, methods_dict: Dict[str, Any], technical_id: str,
                       cls_instance: Any, entity: Any, tools: List[Dict[str, Any]],
                       model: Any, messages: List[AIMessage], tool_choice: str = "auto",
                       response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Main method to run the Google ADK agent.
        
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
            tool_choice: Tool choice strategy
            response_format: Optional response format with schema for validation

        Returns:
            Agent response as string
        """
        if not ADK_AVAILABLE:
            logger.error("Google ADK not available")
            return "Google ADK not installed. Please install the google-adk package."

        try:
            # Setup execution context
            context = AdkAgentContext(
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
                function_tools, model, adapted_messages, response_format
            )
            
            # Execute agent with proper configuration
            result = await self._execute_agent(
                agent, adapted_messages, technical_id
            )
            
            # Process and return result using adapters
            return await self._process_agent_result(
                result, response_format, function_tools, model, adapted_messages
            )

        except Exception as e:
            logger.exception(f"Unexpected error in Google ADK agent execution: {e}")
            return f"Unexpected error occurred: {str(e)}"
        finally:
            logger.debug("ADK run completed")

    def _create_configured_agent(self, function_tools: List[Any], model: Any,
                                adapted_messages: List[Dict[str, str]],
                                response_format: Optional[Dict[str, Any]]) -> Any:
        """
        Create agent with proper configuration using adapters.
        
        Args:
            function_tools: List of FunctionTool objects
            model: Model configuration
            adapted_messages: Adapted message history
            response_format: Optional response format
            
        Returns:
            Configured Agent object
        """
        if not ADK_AVAILABLE:
            raise RuntimeError("Google ADK not available")

        # Extract model configuration
        model_config = self._extract_model_config(model)
        
        # Create LiteLLM model for Google ADK
        adk_model = LiteLlm(
            model_name=model_config['name'],
            temperature=model_config['temperature'],
            max_tokens=model_config['max_tokens']
        )
        
        # Create agent with Google ADK
        agent = Agent(
            model=adk_model,
            tools=function_tools,
            system_instruction="You are a helpful assistant that can use tools to complete tasks."
        )
        
        return agent

    def _extract_model_config(self, model: Any) -> Dict[str, Any]:
        """Extract model configuration parameters."""
        return {
            'name': getattr(model, 'model_name', 'gpt-4o-mini'),
            'temperature': getattr(model, 'temperature', 0.7),
            'max_tokens': getattr(model, 'max_tokens', None),
            'top_p': getattr(model, 'top_p', None)
        }

    async def _execute_agent(self, agent: Any, adapted_messages: List[Dict[str, str]],
                            technical_id: str) -> Any:
        """Execute the agent with proper configuration."""
        if not ADK_AVAILABLE:
            raise RuntimeError("Google ADK not available")

        # Ensure we have valid input
        if not adapted_messages:
            adapted_messages = [self.message_adapter.create_default_message()]

        logger.info(f"Running ADK agent with {len(agent.tools) if hasattr(agent, 'tools') and agent.tools else 0} tools "
                   f"and {len(adapted_messages)} messages")
        logger.debug(f"Message history: {[msg.get('role', 'unknown') for msg in adapted_messages]}")

        # Create session for Google ADK
        session_service = InMemorySessionService()
        session_id = f"adk_session_{technical_id}"
        
        # Google ADK execution pattern
        runner = Runner(agent=agent, session_service=session_service)
        
        # Convert messages to ADK format and run
        user_input = adapted_messages[-1]['content'] if adapted_messages else "Please help me."
        
        result = await runner.run(
            session_id=session_id,
            user_input=user_input,
            max_turns=self.max_calls
        )
        
        return result

    async def _process_agent_result(self, result: Any, response_format: Optional[Dict[str, Any]],
                                   function_tools: List[Any], model: Any,
                                   adapted_messages: List[Dict[str, str]]) -> str:
        """Process agent execution result using adapters."""
        # Extract response from ADK result
        if hasattr(result, 'messages') and result.messages:
            response = str(result.messages[-1].content) if result.messages[-1].content else ""
        elif hasattr(result, 'content'):
            response = str(result.content)
        else:
            response = str(result)
            
        logger.info("ADK Agent completed successfully")
        logger.debug(f"Raw ADK agent response: {response}")

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
                response, response_format["schema"], function_tools, model, adapted_messages
            )

        return response

    async def _validate_and_retry_schema(self, response: str, schema: Dict[str, Any],
                                        function_tools: List[Any], model: Any,
                                        adapted_messages: List[Dict[str, str]]) -> str:
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
                        function_tools, model, correction_messages, {"schema": schema}
                    )

                    # Execute retry
                    retry_result = await self._execute_agent(retry_agent, correction_messages, "retry")
                    
                    # Extract response from retry result
                    if hasattr(retry_result, 'messages') and retry_result.messages:
                        response = str(retry_result.messages[-1].content) if retry_result.messages[-1].content else ""
                    else:
                        response = str(retry_result)

                except Exception as e:
                    logger.exception(f"Error during validation retry {attempt}: {e}")
                    break

        # If all retries failed, return the last response with a warning
        logger.error(f"Schema validation failed after {self.max_calls} attempts. Returning last response.")
        return response
