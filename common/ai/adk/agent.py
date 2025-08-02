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
    from google.genai import types
    ADK_AVAILABLE = True
except ImportError:
    Agent = Any
    Runner = Any
    InMemorySessionService = Any
    # Create mock types for when ADK is not available
    class MockTypes:
        class Content:
            def __init__(self, role, parts):
                self.role = role
                self.parts = parts
        class Part:
            def __init__(self, text):
                self.text = text
        class GenerateContentConfig:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
    types = MockTypes()
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

        # Initialize session service like the deprecated version
        if ADK_AVAILABLE:
            self.session_service = InMemorySessionService()
        else:
            self.session_service = None

        # Initialize adapters with dependency injection
        self.ui_function_handler = AdkUiFunctionHandler()
        self.message_adapter = AdkMessageAdapter()
        self.tool_adapter = AdkToolAdapter(self.ui_function_handler)
        self.schema_adapter = AdkSchemaAdapter()

        # Session cache like the deprecated version
        self._session_cache = {}

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
        Create agent with proper configuration using ADK patterns.

        Args:
            function_tools: List of FunctionTool objects
            model: Model configuration
            adapted_messages: Adapted message history
            response_format: Optional response format

        Returns:
            Configured Agent object
        """
        if not ADK_AVAILABLE:
            logger.warning("Google ADK not available, returning mock agent")
            class MockAgent:
                def __init__(self, model_name, tools):
                    self.model = model_name
                    self.tools = tools
                    self.name = "mock_agent"
            model_config = self._extract_model_config(model)
            return MockAgent(model_config['name'], function_tools)

        # Extract model configuration
        model_config = self._extract_model_config(model)

        # Create instructions based on response format and UI functions
        instructions = self._create_instructions(response_format, function_tools)

        # Create GenerateContentConfig for model settings
        generate_content_config = types.GenerateContentConfig(
            temperature=model_config['temperature'],
            max_output_tokens=model_config['max_tokens'],
            top_p=model_config['top_p'],
            top_k=model_config['top_k']
        )

        # Create agent with Google ADK (use model name directly for Gemini)
        agent = Agent(
            model=model_config['name'],
            name=f"workflow_agent_{hash(str(function_tools)) % 10000}",
            description='Workflow assistant with tools support',
            instruction=instructions,
            generate_content_config=generate_content_config,
            tools=function_tools
        )

        logger.info(f"Created ADK agent with model: {model_config['name']}")
        return agent

    def _extract_model_config(self, model: Any) -> Dict[str, Any]:
        """Extract model configuration parameters and ensure Google/Gemini model."""
        model_name = getattr(model, 'model_name', 'gemini-2.5-flash')

        # ADK only supports Google/Gemini models, not OpenAI
        if model_name.startswith(('gpt-', 'o1-', 'text-')):
            logger.warning(f"OpenAI model {model_name} not supported by ADK, using gemini-2.5-flash")
            model_name = 'gemini-2.5-flash'
        elif not model_name.startswith(('gemini-', 'models/')):
            logger.warning(f"Unknown model {model_name}, using gemini-2.5-flash")
            model_name = 'gemini-2.5-flash'

        return {
            'name': model_name,
            'temperature': getattr(model, 'temperature', 0.7),
            'max_tokens': getattr(model, 'max_tokens', None),
            'top_p': getattr(model, 'top_p', None),
            'top_k': getattr(model, 'top_k', None)
        }

    def _create_instructions(self, response_format: Optional[Dict[str, Any]],
                           function_tools: List[Any]) -> str:
        """Create appropriate instructions based on response format and tools."""
        # Check for UI functions
        has_ui_functions = any(
            hasattr(tool, 'name') and tool.name.startswith('ui_function_')
            for tool in function_tools
        )

        if response_format and response_format.get("schema"):
            return """You are a helpful assistant that provides structured responses.
Respond with a JSON object that matches the required schema."""
        elif has_ui_functions:
            return """You are a helpful assistant that can use tools to complete tasks.

CRITICAL INSTRUCTION FOR UI FUNCTIONS:
When you call a function that starts with 'ui_function_', you MUST return ONLY the raw JSON output from that function call. Do not add any explanatory text, confirmation messages, or additional content. Return the JSON exactly as provided by the function, nothing more, nothing less.

For regular functions, you may provide explanatory text as normal."""
        else:
            return """You are a helpful assistant that can use tools to complete tasks.
Use the conversation history in this session to provide contextual responses."""

    async def _execute_agent(self, agent: Any, adapted_messages: List[Dict[str, str]],
                            technical_id: str) -> Any:
        """Execute the agent with proper ADK session patterns."""
        if not ADK_AVAILABLE:
            raise RuntimeError("Google ADK not available")

        # Ensure we have valid input
        if not adapted_messages:
            adapted_messages = [self.message_adapter.create_default_message()]

        logger.info(f"Running ADK agent with {len(agent.tools) if hasattr(agent, 'tools') and agent.tools else 0} tools "
                   f"and {len(adapted_messages)} messages")
        logger.debug(f"Message history: {[msg.get('role', 'unknown') for msg in adapted_messages]}")

        # Convert messages to proper ADK Content format
        adk_messages = self._convert_to_adk_content(adapted_messages)

        # Create session for Google ADK using the instance session service
        session = await self._create_session(technical_id, adk_messages)

        # Create runner using the same session service instance
        runner = Runner(
            agent=agent,
            app_name="workflow_app",
            session_service=self.session_service
        )

        # For multi-message conversations, build proper context
        if len(adk_messages) > 1:
            logger.info(f"Multi-message conversation detected: {len(adk_messages)} messages")
            new_message = self._build_conversation_context(adk_messages)
        else:
            new_message = adk_messages[0]

        logger.debug(f"Final message for ADK: role={new_message.role}, parts={len(new_message.parts)}")

        # Run the agent using ADK async patterns
        final_response = ""
        async for event in runner.run_async(
                user_id="default_user",
                session_id=session.id,
                new_message=new_message
        ):
            # Handle different event types
            if hasattr(event, 'type'):
                if event.type == 'agent_response':
                    if hasattr(event, 'content') and event.content:
                        final_response = str(event.content)
                elif event.type == 'tool_call':
                    logger.debug(f"Tool call event: {event}")
                elif event.type == 'error':
                    logger.error(f"ADK error event: {event}")
            else:
                # Fallback for different event structures
                final_response = str(event)

        return final_response or "No response from ADK agent"

    def _convert_to_adk_content(self, adapted_messages: List[Dict[str, str]]) -> List[Any]:
        """Convert adapted messages to ADK Content format."""
        if not ADK_AVAILABLE:
            logger.warning("ADK not available, returning adapted messages as-is")
            return adapted_messages

        adk_messages = []
        for message in adapted_messages:
            role = message.get('role', 'user')
            content = message.get('content', '')

            # Map roles properly for ADK
            if role == 'assistant':
                role = 'model'  # ADK uses 'model' instead of 'assistant'
            elif role not in ['user', 'model', 'system']:
                logger.warning(f"Unknown role '{role}', defaulting to 'user'")
                role = 'user'

            adk_messages.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=content)]
                )
            )
        return adk_messages

    async def _create_session(self, technical_id: str, adk_messages: List[Any]) -> Any:
        """Create ADK session with proper initialization following deprecated patterns."""
        if not ADK_AVAILABLE:
            logger.warning("ADK not available, returning mock session")
            class MockSession:
                def __init__(self, session_id):
                    self.id = session_id
            return MockSession(f"adk_session_{technical_id}")

        session_id = f"adk_session_{technical_id}"

        # Check if session already exists in cache (like deprecated version)
        if session_id in self._session_cache:
            logger.debug(f"Using cached session: {session_id}")
            return self._session_cache[session_id]

        # Create session with required app_name parameter
        session = await self.session_service.create_session(
            session_id=session_id,
            user_id="default_user",
            app_name="workflow_app"  # Required parameter that was missing
        )

        # Cache the session like the deprecated version
        self._session_cache[session_id] = session
        logger.debug(f"Created and cached new session: {session_id}")

        return session

    def _build_conversation_context(self, adk_messages: List[Any]) -> Any:
        """Build conversation context for multi-message conversations."""
        # For ADK, we provide the full conversation context in a single message
        # rather than trying to build it incrementally
        context_parts = []

        if not ADK_AVAILABLE:
            # Handle dict format when ADK is not available
            for i, msg in enumerate(adk_messages[:-1]):  # All but the last message
                role_text = "User" if msg.get('role') == 'user' else "Assistant"
                content = msg.get('content', '')
                context_parts.append(f"{role_text}: {content}")

            # Add the latest message
            latest_msg = adk_messages[-1]
            latest_text = latest_msg.get('content', '')

            # Combine context with latest message
            if context_parts:
                full_context = "Previous conversation:\n" + "\n".join(context_parts) + f"\n\nCurrent request: {latest_text}"
            else:
                full_context = latest_text

            return {"role": latest_msg.get('role', 'user'), "content": full_context}
        else:
            # Handle ADK Content objects
            for i, msg in enumerate(adk_messages[:-1]):  # All but the last message
                role_text = "User" if msg.role == 'user' else "Assistant"
                for part in msg.parts:
                    if hasattr(part, 'text'):
                        context_parts.append(f"{role_text}: {part.text}")

            # Add the latest message
            latest_msg = adk_messages[-1]
            latest_text = ""
            for part in latest_msg.parts:
                if hasattr(part, 'text'):
                    latest_text += part.text

            # Combine context with latest message
            if context_parts:
                full_context = "Previous conversation:\n" + "\n".join(context_parts) + f"\n\nCurrent request: {latest_text}"
            else:
                full_context = latest_text

            return types.Content(
                role=latest_msg.role,
                parts=[types.Part(text=full_context)]
            )

    async def _process_agent_result(self, result: Any, response_format: Optional[Dict[str, Any]],
                                   function_tools: List[Any], model: Any,
                                   adapted_messages: List[Dict[str, str]]) -> str:
        """Process agent execution result using adapters."""
        # ADK result is already a string from our execution method
        response = str(result) if result else ""

        logger.info("ADK Agent completed successfully")
        logger.debug(f"Raw ADK agent response: {response}")

        # Check if response itself is UI function JSON
        if self.ui_function_handler.is_ui_function_json(response.strip()):
            logger.debug("Response is direct UI function JSON")
            return response.strip()

        # Try to extract UI function from response content
        ui_result = self.ui_function_handler.extract_ui_function_result(response)
        if ui_result:
            logger.debug("Extracted UI function from response content")
            return ui_result

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
