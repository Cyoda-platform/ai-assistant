import json

from common.config.config import config
from entity.chat.model.chat import ChatEntity
from entity.model import ModelConfig


#todo add react, prompt chaining etc - other techniques, add more implementations
class OpenAiAgent:
    def __init__(self, client, max_calls=config.MAX_AI_AGENT_ITERATIONS):
        """
        Initialize the AiAgent with a maximum number of API calls and a model name.
        """
        self.client = client
        self.max_calls = max_calls

    def adapt_messages(self, messages):
        for message in messages:
            if isinstance(message, dict) and message.get("content"):
                content = message.get("content")
                if isinstance(content, list):
                    # Join list elements into a single string, using a space as a separator.
                    message["content"] = " ".join(content)
        return messages

    async def run_agent(self, methods_dict, technical_id, cls_instance, entity: ChatEntity, tools, model: ModelConfig, messages, tool_choice="auto", response_format=None):
        # Loop until a final answer is received or maximum calls are reached.
        messages = self.adapt_messages(messages)
        ai_response_format = {"type": "json_schema",
                              "json_schema": response_format} if response_format else None
        for call_number in range(self.max_calls):
            completion = await self.client.create_completion(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                response_format=ai_response_format

            )

            # Get the response message.
            response_message = completion.choices[0].message

            # If there are tool calls, process each one.
            if hasattr(response_message, "tool_calls") and response_message.tool_calls:
                # Append the assistant's message (which contains tool_calls) to the conversation.
                messages.append(response_message)

                # Process every tool call in the message.
                for tool_call in response_message.tool_calls:
                    # Extract the arguments from the tool call (assumed to be JSON).
                    args = json.loads(tool_call.function.arguments)

                    # Look up the actual function implementation in the original tools list.
                    result = await methods_dict[tool_call.function.name](cls_instance, technical_id=technical_id, entity=entity, **args)

                    # Append a separate tool message for this tool call.
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
            else:
                messages.append({"role": "assistant", "content": response_message.content})
                return response_message.content

        # Return the last message if max_calls is reached.
        response = "Max iterations limit reached. Let's proceed to the next iteration"
        messages.append({"role": "assistant", "content": response})
        return response

