import json
import logging

import jsonschema
from jsonschema import ValidationError

from common.config import const
from common.config.config import config
from entity.model import AIMessage

logger = logging.getLogger(__name__)


# todo add react, prompt chaining etc - other techniques, add more implementations
class OpenAiAgent:
    def __init__(self, client, max_calls=config.MAX_AI_AGENT_ITERATIONS):
        """
        Initialize the AiAgent with a maximum number of API calls and a model name.
        """
        self.client = client
        self.max_calls = max_calls

    def adapt_messages(self, messages):
        adapted_messages = []
        for message in messages:
            if isinstance(message, AIMessage):
                content = message.content
                if content:
                    adapted_message = {
                        "role": message.role,
                        "content": " ".join(content) if isinstance(content, list) else content
                    }
                    adapted_messages.append(adapted_message)
            else:
                logger.exception(f"Wrong message type {message}")

        return adapted_messages

    async def _validate_with_schema(
            self, adapted_messages: list, content: str, schema: dict, attempt: int, max_retries: int
    ):
        try:
            parsed = json.loads(content)
            # todo get all validation errors at once
            jsonschema.validate(instance=parsed, schema=schema)
            # Return the original string on success
            return content, None
        except (json.JSONDecodeError, ValidationError) as e:
            error = str(e)
            error = (error[:50] + '...') if len(error) > 20 else error
            msg = f"Validation failed on attempt {attempt}/{max_retries}: {error}. Please return correct json. "
            if attempt > 2:
                msg = f"{msg}. If the task is too hard you can make the code shorter. Just ensure you return correct json."
            adapted_messages.append({"role": "user", "content": msg})
            return None, msg

    async def run_agent(
            self, methods_dict, technical_id, cls_instance, entity, tools, model,
            messages, tool_choice="auto", response_format=None
    ):
        adapted_messages = self.adapt_messages(messages)
        schema = response_format.get("schema") if response_format else None
        max_retries = self.max_calls

        for attempt in range(1, max_retries + 1):
            ai_response_format = (
                {"type": "json_schema", "json_schema": response_format}
                if response_format else None
            )
            logger.info(f"Running completion...attempt={attempt}")
            completion = await self.client.create_completion(
                model=model,
                messages=adapted_messages,
                tools=tools,
                tool_choice=tool_choice,
                response_format=ai_response_format
            )
            resp = completion.choices[0].message

            if hasattr(resp, "tool_calls") and resp.tool_calls:
                adapted_messages.append(resp)
                for call in resp.tool_calls:
                    args = json.loads(call.function.arguments)
                    if call.function.name.startswith(const.UI_FUNCTION_PREFIX):
                        if isinstance(args, dict):
                            return json.dumps({"type": const.UI_FUNCTION_PREFIX, "function": call.function.name, **args})
                        return json.dumps({"type": const.UI_FUNCTION_PREFIX, "function": call.function.name})
                    result = await methods_dict[call.function.name](
                        cls_instance, technical_id=technical_id, entity=entity, **args
                    )
                    adapted_messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": str(result)
                    })
                    if call.function.name == const.Notifications.EXIT_LOOP_FUNCTION_NAME.value:
                        content =  f'{resp.content} \n {const.Notifications.PROCEED_TO_THE_NEXT_STEP.value}'
                        adapted_messages.append(
                            {"role": "assistant", "content": content})
                        return content
                continue

            content = resp.content

            if schema:
                valid_str, error = await self._validate_with_schema(
                    adapted_messages, content, schema, attempt, max_retries
                )
                if valid_str is not None:
                    # Always return the JSON string
                    adapted_messages.append({"role": "assistant", "content": content})
                    return valid_str
                # otherwise retry
            else:
                # No schema: return string as before
                adapted_messages.append({"role": "assistant", "content": content})
                return content
        logger.exception(f"error:Max validation retries reached last_response: {messages[-1]["content"]}")
        return "Something fishy happening with the LLM..."
