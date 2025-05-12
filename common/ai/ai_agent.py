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
            self, messages: list, content: str, schema: dict, attempt: int, max_retries: int
    ):
        try:
            parsed = json.loads(content)
            jsonschema.validate(instance=parsed, schema=schema)
            # Return the original string on success
            return content, None
        except (json.JSONDecodeError, ValidationError) as e:
            msg = f"Validation failed on attempt {attempt}/{max_retries}: {e}. Retrying..."
            messages.append({"role": "assistant", "content": msg})
            return None, msg


    async def run_agent(
            self, methods_dict, technical_id, cls_instance, entity, tools, model,
            messages, tool_choice="auto", response_format=None
    ):
        messages = self.adapt_messages(messages)
        schema = response_format.get("schema") if response_format else None
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            ai_response_format = (
                {"type": "json_schema", "json_schema": schema}
                if schema else None
            )

            completion = await self.client.create_completion(
                model=model, messages=messages, tools=tools,
                tool_choice=tool_choice, response_format=ai_response_format
            )
            resp = completion.choices[0].message

            if hasattr(resp, "tool_calls") and resp.tool_calls:
                messages.append(resp)
                for call in resp.tool_calls:
                    args = json.loads(call.function.arguments)
                    result = await methods_dict[call.function.name](
                        cls_instance, technical_id=technical_id, entity=entity, **args
                    )
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": str(result)
                    })
                continue

            content = resp.content
            messages.append({"role": "assistant", "content": content})

            if schema:
                valid_str, error = await self._validate_with_schema(
                    messages, content, schema, attempt, max_retries
                )
                if valid_str is not None:
                    # Always return the JSON string
                    return valid_str
                # otherwise retry
            else:
                # No schema: return string as before
                return content

        return {
            "error": "Max validation retries reached",
            "last_response": messages[-1]["content"]
        }