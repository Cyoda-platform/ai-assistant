import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
import os

import jsonschema
from jsonschema import ValidationError
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


class AdkAgent:
    """
    Google ADK-based AI Agent that provides an alternative to OpenAiAgent.
    Supports both OpenAI models (via LiteLlm) and Gemini models (direct).
    Includes MCP (Model Context Protocol) tool support.
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
        self.mcp_tools = []

    def adapt_messages(self, messages):
        """Convert AIMessage objects to ADK-compatible format"""
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
                logger.exception(f"Wrong message type {message}")
        return adapted_messages

    def _create_function_tools(self, tools, methods_dict):
        """Convert JSON tool definitions to ADK FunctionTool objects"""
        function_tools = []
        
        for tool in tools or []:
            if tool.get("type") == "function":
                func_def = tool.get("function", {})
                func_name = func_def.get("name")
                
                if func_name in methods_dict:
                    # Store tool definition for later context binding
                    function_tools.append({
                        'type': 'function',
                        'name': func_name,
                        'method': methods_dict[func_name],
                        'description': func_def.get("description", ""),
                        'parameters': func_def.get("parameters", {})
                    })
            elif tool.get("type") == "mcp":
                # Handle MCP tool definitions from JSON config
                mcp_def = tool.get("mcp", {})
                function_tools.append({
                    'type': 'mcp',
                    'server_name': mcp_def.get("server_name"),
                    'command': mcp_def.get("command", []),
                    'args': mcp_def.get("args", []),
                    'env': mcp_def.get("env", {}),
                    'description': mcp_def.get("description", "")
                })
        
        return function_tools

    def _create_mcp_tools(self):
        """Create MCP tools from configured servers"""
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
                        # Create actual MCPTool instance
                        mcp_tool = MCPTool(
                            command=config["command"],
                            args=config.get("args", []),
                            env=config.get("env", {})
                        )
                        mcp_tools.append(mcp_tool)
                        logger.info(f"Created MCPTool for server: {server_name}")
                    else:
                        # Create mock MCP tool info for configuration
                        mcp_tool_info = {
                            "type": "mcp_server",
                            "server_name": server_name,
                            "command": config["command"],
                            "args": config.get("args", []),
                            "description": config["description"]
                        }
                        mcp_tools.append(mcp_tool_info)
                        logger.info(f"Configured MCP server (mock): {server_name}")

                    logger.info(f"  Command: {config['command']}")
                    logger.info(f"  Description: {config['description']}")

                except Exception as e:
                    logger.error(f"Failed to configure MCP server {server_name}: {e}")
            else:
                logger.warning(f"Unknown MCP server: {server_name}")

        self.mcp_tools = mcp_tools
        logger.info(f"Configured {len(mcp_tools)} MCP servers")
        return mcp_tools

    async def _validate_with_schema(
            self, content: str, schema: dict, attempt: int, max_retries: int
    ):
        """Validate response against JSON schema"""
        try:
            parsed = json.loads(content)
            jsonschema.validate(instance=parsed, schema=schema)
            return content, None
        except (json.JSONDecodeError, ValidationError) as e:
            error = str(e)
            error = (error[:50] + '...') if len(error) > 20 else error
            msg = f"Validation failed on attempt {attempt}/{max_retries}: {error}. Please return correct json. "
            if attempt > 2:
                msg = f"{msg}. If the task is too hard you can make the code shorter. Just ensure you return correct json."
            return None, msg

    async def run_agent(
            self, methods_dict, technical_id, cls_instance, entity, tools, model,
            messages, tool_choice="auto", response_format=None
    ):
        """Main method to run the ADK agent"""
        try:
            # Convert messages to ADK format
            adapted_messages = self.adapt_messages(messages)
            
            # Create function tools from JSON definitions with context
            tool_definitions = self._create_function_tools(tools, methods_dict)
            
            # Create actual tool objects with proper context
            all_tools = []
            
            for tool_def in tool_definitions:
                if isinstance(tool_def, dict):
                    if tool_def.get('type') == 'function':
                        # Handle function tools
                        def create_contextual_wrapper(name, method, description, technical_id, entity, cls_instance):
                            async def tool_wrapper(**kwargs):
                                try:
                                    result = await method(
                                        cls_instance, 
                                        technical_id=technical_id, 
                                        entity=entity, 
                                        **kwargs
                                    )
                                    return str(result)
                                except Exception as e:
                                    logger.exception(f"Error in tool {name}: {e}")
                                    return f"Error executing {name}: {str(e)}"
                            
                            tool_wrapper.__name__ = name
                            tool_wrapper.__doc__ = description
                            return tool_wrapper
                        
                        wrapper = create_contextual_wrapper(
                            tool_def['name'],
                            tool_def['method'],
                            tool_def['description'],
                            technical_id,
                            entity,
                            cls_instance
                        )
                        all_tools.append(FunctionTool(func=wrapper))
                        
                    elif tool_def.get('type') == 'mcp':
                        # Handle MCP tools from JSON config
                        logger.info(f"MCP tool configured from JSON: {tool_def['server_name']}")
                        logger.info(f"  Command: {tool_def['command']}")
                        logger.info(f"  Args: {tool_def['args']}")
                        logger.info(f"  Description: {tool_def['description']}")
                        # TODO: Create actual MCP tool when session management is implemented
                        
                else:
                    # Already a tool object
                    all_tools.append(tool_def)
            
            # Add MCP tools from agent configuration (self.mcp_servers)
            agent_mcp_tools = self._create_mcp_tools()
            all_tools.extend(agent_mcp_tools)

            # Determine the model name and configure for OpenAI if needed
            model_name = model.model_name if hasattr(model, 'model_name') else 'gemini-2.0-flash'
            
            # Configure model based on provider
            if model_name.startswith(('gpt-', 'o1-', 'text-')):
                # For OpenAI models, use LiteLlm wrapper
                if not os.getenv('OPENAI_API_KEY'):
                    logger.warning("OpenAI model specified but OPENAI_API_KEY not set")
                
                # Use LiteLlm wrapper for OpenAI models
                model_instance = LiteLlm(model=f"openai/{model_name}")
                logger.info(f"Using OpenAI model via LiteLlm: {model_name}")
            else:
                # For Gemini models, use model name directly
                model_instance = model_name
                logger.info(f"Using Gemini model: {model_name}")
            
            # Create ADK agent with all tools (existing + MCP)
            agent = Agent(
                model=model_instance,
                name='workflow_agent',
                instruction='You are a helpful assistant that can use tools to complete tasks. You have access to both workflow-specific tools and external services via MCP.',
                tools=all_tools
            )
            
            # Create session
            session = await self.session_service.create_session(
                app_name="workflow_app",
                user_id="default_user",
                session_id=f"session_{technical_id}"
            )
            
            # Create runner
            runner = Runner(
                agent=agent,
                app_name="workflow_app",
                session_service=self.session_service
            )
            
            # Get the last message as the new message
            if adapted_messages:
                new_message = adapted_messages[-1]
            else:
                new_message = types.Content(
                    role='user',
                    parts=[types.Part(text="Please help me.")]
                )
            
            # Run the agent
            events = runner.run_async(
                user_id="default_user",
                session_id=session.id,
                new_message=new_message
            )
            
            # Process events and collect response
            final_response = ""
            tool_calls_made = []

            async for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            final_response += part.text
                        elif part.function_call:
                            # Handle function calls
                            func_call = part.function_call
                            if func_call.name and func_call.name.startswith(const.UI_FUNCTION_PREFIX):
                                # Handle UI functions
                                args = func_call.args or {}
                                return json.dumps({
                                    "type": const.UI_FUNCTION_PREFIX,
                                    "function": func_call.name,
                                    **args
                                })

                            # Execute the actual tool call
                            if func_call.name in methods_dict:
                                try:
                                    args = func_call.args or {}
                                    result = await methods_dict[func_call.name](
                                        cls_instance,
                                        technical_id=technical_id,
                                        entity=entity,
                                        **args
                                    )
                                    logger.info(f"Tool {func_call.name} executed successfully: {result}")
                                    # Add tool result to response
                                    final_response += f"\nTool {func_call.name} result: {result}"
                                except Exception as e:
                                    logger.exception(f"Error executing tool {func_call.name}: {e}")
                                    final_response += f"\nTool {func_call.name} error: {str(e)}"
                            else:
                                logger.warning(f"Tool {func_call.name} not found in methods_dict")
                                final_response += f"\nTool {func_call.name} not available"

                            tool_calls_made.append(func_call)

                # Check for final response
                if event.is_final_response():
                    break
            
            # Handle schema validation if required
            if response_format and response_format.get("schema"):
                schema = response_format["schema"]
                for attempt in range(1, self.max_calls + 1):
                    valid_str, error = await self._validate_with_schema(
                        final_response, schema, attempt, self.max_calls
                    )
                    if valid_str is not None:
                        return valid_str
                    
                    # If validation failed, we would need to retry with ADK
                    # For now, return the error
                    logger.error(f"Schema validation failed: {error}")
                    break
            
            return final_response or "Task completed successfully."
            
        except Exception as e:
            logger.exception(f"Error in ADK agent execution: {e}")
            raise
