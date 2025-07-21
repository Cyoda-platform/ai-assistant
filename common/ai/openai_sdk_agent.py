import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
import os

import jsonschema
from jsonschema import ValidationError
from openai import AsyncOpenAI
from openai.types.beta import Assistant, Thread
from openai.types.beta.threads import Run, Message

from common.config import const
from common.config.config import config
from entity.model import AIMessage

logger = logging.getLogger(__name__)


class OpenAiSdkAgent:
    """
    OpenAI SDK-based AI Agent using OpenAI's official Assistants API.
    Provides advanced features like persistent threads, built-in tool calling,
    and native OpenAI integrations.
    """
    
    def __init__(self, max_calls=config.MAX_AI_AGENT_ITERATIONS):
        """
        Initialize the OpenAI SDK Agent.
        
        Args:
            max_calls: Maximum number of agent iterations
        """
        self.max_calls = max_calls
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.assistant = None
        self.thread = None

    async def _create_assistant(self, tools, model, instructions):
        """Create or update OpenAI Assistant"""
        try:
            # Convert tools to OpenAI format
            openai_tools = []
            
            for tool in tools or []:
                if tool.get("type") == "function":
                    openai_tools.append({
                        "type": "function",
                        "function": tool.get("function", {})
                    })
            
            # Add built-in OpenAI tools
            openai_tools.extend([
                {"type": "code_interpreter"},
                {"type": "file_search"}
            ])
            
            # Create assistant
            self.assistant = await self.client.beta.assistants.create(
                name="Workflow Assistant",
                instructions=instructions,
                model=model.model_name if hasattr(model, 'model_name') else 'gpt-4o',
                tools=openai_tools
            )
            
            logger.info(f"Created OpenAI Assistant: {self.assistant.id}")
            return self.assistant
            
        except Exception as e:
            logger.exception(f"Error creating OpenAI Assistant: {e}")
            raise

    async def _create_thread(self):
        """Create OpenAI Thread for conversation"""
        try:
            self.thread = await self.client.beta.threads.create()
            logger.info(f"Created OpenAI Thread: {self.thread.id}")
            return self.thread
        except Exception as e:
            logger.exception(f"Error creating OpenAI Thread: {e}")
            raise

    async def _add_message_to_thread(self, content: str, role: str = "user"):
        """Add message to thread"""
        try:
            message = await self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=content
            )
            return message
        except Exception as e:
            logger.exception(f"Error adding message to thread: {e}")
            raise

    async def _run_assistant(self, instructions: str = None, methods_dict=None, technical_id=None, entity=None, cls_instance=None):
        """Run the assistant on the thread"""
        try:
            run = await self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions
            )

            # Wait for completion
            while run.status in ['queued', 'in_progress', 'requires_action']:
                await asyncio.sleep(1)
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=run.id
                )

                # Handle tool calls
                if run.status == 'requires_action':
                    await self._handle_tool_calls(run, methods_dict, technical_id, entity, cls_instance)

            if run.status == 'completed':
                return await self._get_latest_message()
            else:
                logger.error(f"Run failed with status: {run.status}")
                return f"Assistant run failed: {run.status}"

        except Exception as e:
            logger.exception(f"Error running assistant: {e}")
            raise

    async def _handle_tool_calls(self, run, methods_dict=None, technical_id=None, entity=None, cls_instance=None):
        """Handle tool calls from the assistant"""
        try:
            tool_outputs = []

            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                if tool_call.type == "function":
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Handle UI functions
                    if function_name.startswith(const.UI_FUNCTION_PREFIX):
                        result = json.dumps({
                            "type": const.UI_FUNCTION_PREFIX,
                            "function": function_name,
                            **function_args
                        })
                    else:
                        # Execute the actual tool call
                        if methods_dict and function_name in methods_dict:
                            try:
                                tool_result = await methods_dict[function_name](
                                    cls_instance,
                                    technical_id=technical_id,
                                    entity=entity,
                                    **function_args
                                )
                                result = str(tool_result)
                                logger.info(f"Tool {function_name} executed successfully: {result}")
                            except Exception as e:
                                logger.exception(f"Error executing tool {function_name}: {e}")
                                result = f"Error executing {function_name}: {str(e)}"
                        else:
                            logger.warning(f"Tool {function_name} not found in methods_dict")
                            result = f"Tool {function_name} not available"

                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": result
                    })

            # Submit tool outputs
            await self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=self.thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        except Exception as e:
            logger.exception(f"Error handling tool calls: {e}")
            raise

    async def _get_latest_message(self):
        """Get the latest assistant message from the thread"""
        try:
            messages = await self.client.beta.threads.messages.list(
                thread_id=self.thread.id,
                order="desc",
                limit=1
            )
            
            if messages.data:
                message = messages.data[0]
                if message.role == "assistant":
                    # Extract text content
                    content = ""
                    for content_block in message.content:
                        if content_block.type == "text":
                            content += content_block.text.value
                    return content
            
            return "No response from assistant"
            
        except Exception as e:
            logger.exception(f"Error getting latest message: {e}")
            return f"Error retrieving response: {e}"

    def adapt_messages(self, messages):
        """Convert AIMessage objects to content strings"""
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
                logger.exception(f"Wrong message type {message}")
        return adapted_messages

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
        """Main method to run the OpenAI SDK agent"""
        try:
            # Convert messages
            adapted_messages = self.adapt_messages(messages)
            
            # Create assistant if not exists
            if not self.assistant:
                instructions = "You are a helpful assistant that can use tools to complete tasks."
                await self._create_assistant(tools, model, instructions)
            
            # Create thread if not exists
            if not self.thread:
                await self._create_thread()
            
            # Add messages to thread
            for msg in adapted_messages:
                await self._add_message_to_thread(
                    content=msg["content"],
                    role=msg["role"]
                )
            
            # Run assistant
            response = await self._run_assistant(
                methods_dict=methods_dict,
                technical_id=technical_id,
                entity=entity,
                cls_instance=cls_instance
            )

            # Handle schema validation if required
            if response_format and response_format.get("schema"):
                schema = response_format["schema"]
                for attempt in range(1, self.max_calls + 1):
                    valid_str, error = await self._validate_with_schema(
                        response, schema, attempt, self.max_calls
                    )
                    if valid_str is not None:
                        return valid_str

                    # If validation failed, add correction message and retry
                    await self._add_message_to_thread(
                        content=f"The previous response had validation errors: {error}",
                        role="user"
                    )
                    response = await self._run_assistant(
                        methods_dict=methods_dict,
                        technical_id=technical_id,
                        entity=entity,
                        cls_instance=cls_instance
                    )
                
                # If all retries failed
                raise Exception(f"Max validation retries reached. Last response: {response}")
            
            return response
            
        except Exception as e:
            logger.exception(f"Error in OpenAI SDK agent execution: {e}")
            raise

    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.assistant:
                await self.client.beta.assistants.delete(self.assistant.id)
                logger.info(f"Deleted assistant: {self.assistant.id}")
            
            # Note: Threads are automatically cleaned up by OpenAI
            
        except Exception as e:
            logger.exception(f"Error during cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            if self.assistant:
                # Note: Can't run async in destructor, so just log
                logger.info(f"Assistant {self.assistant.id} should be cleaned up manually")
        except:
            pass
