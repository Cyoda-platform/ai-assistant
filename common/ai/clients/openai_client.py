import json
import logging

from openai import AsyncOpenAI

from common.utils.utils import custom_serializer
from entity.model import ModelConfig, ToolChoice

logger = logging.getLogger(__name__)

class AsyncOpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI()

    async def create_completion(
            self,
            model: ModelConfig,
            messages: list,
            tools: list = None,
            tool_choice: ToolChoice = "auto",
            response_format = None
    ):
        """
        Create a chat completion using the asynchronous OpenAI API.

        Args:
            model (str): The model ID to use.
            messages (list): A list of message dicts in the OpenAI chat format.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum tokens in the completion.
            top_p (float): Nucleus sampling parameter.
            frequency_penalty (float): Frequency penalty.
            presence_penalty (float): Presence penalty.
            tools (list, optional): List of tool definitions (if using OpenAI functions).
            tool_choice (str): How to choose the tool call (default "auto").

        Returns:
            The response from the OpenAI API.
        """
        try:
            logger.info(f"Invoking openai client with messages: {json.dumps(messages[-1], default=custom_serializer)}")
        except Exception as e:
            logger.exception(e)
        if model.model_name in ["o4-mini"]:
            response = await self.client.chat.completions.create(
                model=model.model_name,
                max_completion_tokens=model.max_tokens,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                response_format=response_format
            )
        else:
            try:
                response = await self.client.chat.completions.create(
                    model=model.model_name,
                    temperature=model.temperature,
                    max_tokens=model.max_tokens,
                    top_p=model.top_p,
                    frequency_penalty=model.frequency_penalty,
                    presence_penalty=model.presence_penalty,
                    messages=messages,
                    tools=tools,
                    tool_choice=tool_choice,
                    response_format=response_format
                )
            except Exception as e:
                logger.exception(e)
                raise e
        logger.info(f"Invoked openai client with response: {response}")
        return response
