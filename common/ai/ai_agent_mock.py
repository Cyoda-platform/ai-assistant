# ----- Example Usage -----
import asyncio

from common.config.conts import OPEN_AI
from logic.init import BeanFactory

if __name__ == "__main__":
    # Define the tools list with their actual implementations.
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current temperature for provided coordinates in celsius.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"}
                    },
                    "required": ["latitude", "longitude"],
                    "additionalProperties": False
                },
                "strict": True
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_humidity",
                "description": "Get current humidity for provided coordinates.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"}
                    },
                    "required": ["latitude", "longitude"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    ]

    # Define the initial messages and a system prompt.
    messages = [{"role": "user", "content": "What's the weather and humidity like in Paris today?"}]

    # Create an instance of the agent and run the conversation.
    factory = BeanFactory(config={"CHAT_REPOSITORY": "cyoda"})
    ai_agent = factory.get_services()["ai_agent"]
    workflow_dispatcher = factory.get_services()["workflow_dispatcher"]
    final_answer = asyncio.run(ai_agent.run(
        methods_dict=workflow_dispatcher.methods_dict,
        cls_instance=workflow_dispatcher.cls_instance,
        payload_data={},
        tools=tools,
        messages=messages,
        model=OPEN_AI,
        tool_choice="auto"))
    print("Final Answer:", final_answer)
