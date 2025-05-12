import json
import jsonschema
from jsonschema import ValidationError
from common.config.config import config
from entity.chat.chat import ChatEntity
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


    async def _validate_with_schema(
            self,
            messages: list,
            content: str,
            schema: dict,
            attempt: int,
            max_retries: int
    ):
        """
        Try parsing & validating `content` against `schema`.
        On success, return (parsed_obj, None).
        On failure, append an error note to messages and return (None, error_msg).
        """
        try:
            parsed = json.loads(content)
            jsonschema.validate(instance=parsed, schema=schema)
            return parsed, None
        except (json.JSONDecodeError, ValidationError) as e:
            error_msg = (
                f"Validation failed on attempt {attempt}/{max_retries}: {e}. "
                "Retrying..."
            )
            messages.append({"role": "assistant", "content": error_msg})
            return None, error_msg


    async def run_agent(
            self,
            methods_dict,
            technical_id,
            cls_instance,
            entity: ChatEntity,
            tools,
            model: ModelConfig,
            messages,
            tool_choice="auto",
            response_format=None,
    ):
        messages = self.adapt_messages(messages)
        schema = response_format.get("schema") if response_format else None
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            ai_response_format = (
                {"type": "json_schema", "json_schema": response_format}
                if response_format
                else None
            )

            completion = await self.client.create_completion(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                response_format=ai_response_format,
            )

            response_message = completion.choices[0].message

            # --- existing tool-call handling ---
            if hasattr(response_message, "tool_calls") and response_message.tool_calls:
                messages.append(response_message)
                for tool_call in response_message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    result = await methods_dict[tool_call.function.name](
                        cls_instance, technical_id=technical_id, entity=entity, **args
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
                # loop around for the next assistant reply
                continue

            # --- got a final assistant message ---
            content = response_message.content
            messages.append({"role": "assistant", "content": content})

            # If schema present, validate via helper
            if schema:
                valid_obj, error = await self._validate_with_schema(
                    messages, content, schema, attempt, max_retries
                )
                if valid_obj is not None:
                    return valid_obj
                # else: error appended, retry unless out of attempts
            else:
                # no schema: just return text
                return content

        # out of retries
        return {
            "error": "Max validation retries reached",
            "last_response": messages[-1]["content"]
        }