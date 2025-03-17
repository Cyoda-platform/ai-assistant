import logging
import re

from common.config.config import MAX_ITERATION, VALIDATION_MAX_RETRIES
from common.config.conts import OPEN_AI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ChatBot:
    """
    ChatBot that maintains conversation history and interacts with the OpenAI API.
    """

    def __init__(self, system_prompt, history, ai_client):
        self.client = ai_client  # Ensure your OpenAI API key is properly configured
        self.history = history
        self.history_init_size = len(history)
        self.history.append({"role": "system", "content": system_prompt})

    async def chat(self) -> str:
        """
        Appends the user message to history, calls the API, appends the response, and returns it.
        """
        result = await self._execute()
        self.history.append({"role": "assistant", "content": result})
        return result

    async def _execute(self) -> str:
        try:
            completion = await self.client.chat.completions.create(
                model=OPEN_AI,
                messages=self.history,
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            assistant_response = completion.choices[0].message.content
            logger.info("Assistant response: %s", assistant_response)
            return assistant_response
        except Exception as e:
            logger.exception("Error during completion: %s", e)
            return "Error: Could not get a response from the model."

action_re = re.compile(r'^Action: (\w+): (.+)$', re.MULTILINE)

class AiAgent:
    def __init__(self, tools, mock=False, entity_service=None):
        self.mock = mock
        self.entity_service = entity_service
        self.TOOLS = tools
        self.TOOLS_DESCRIPTION = self.get_tools_description(self.TOOLS.items())
        self.PROMPT = f"""
            You are a highly knowledgeable assistant specialized in code analysis, debugging, and repository management. 
            You operate using a Thought-Action-Observation loop to analyze issues and apply fixes iteratively.

            Guidelines:
            1. Begin your response with "Thought:" to explain your reasoning.
            2. If you need to perform an action (such as reading a file, searching the web, scraping content, or saving changes), output exactly one line in the format:
               "Action: <tool_name>: <input parameters>"
               For example: "Action: read_file: chat_id, filename.py"
            3. For the "example_function" action, you must always include three comma-separated parameters: chat_id, new file contents (in quotes if necessary), and file_name.
            4. Wait for an "Observation:" response before proceeding to further reasoning or actions.
            5. If you can directly provide the final answer, begin your response with "Answer:" followed by your answer.
            6. Always end your final answer with "Answer:" followed by the resolved result or explanation.

            Available Tools:
            {self.TOOLS_DESCRIPTION}

            Examples:

            Example without actions:
            Question: What is the capital of France?
            Thought: I know the answer.
            Answer: Paris

            Example with actions:
            Question: Please fix the file app.py, chat id = 1234
            Thought: I need to read the file first.
            Action: read_file: 1234, app.py
            PAUSE
            [After receiving Observation:]
            Thought: I have analyzed the file. I will now generate the fix.
            Action: save_file: 1234, "new fixed content", app.py
            PAUSE
            [After receiving Observation:]
            Answer: The file app.py has been updated with the fix.

            Always follow these exact formats for actions and final answers.
            """.strip()

    def get_tools_description(self, tools) -> str:
        """
        Generates a dynamic description for each tool.
        """
        descriptions = []
        for name, tool in tools:
            descriptions.append(f"{name}: {tool['description']} {tool['example']}")
        return "\n".join(descriptions)

    def parse_parameters(self, action_input: str) -> list:
        """
        Splits the action input into parameters, treating text wrapped in double quotes
        as a single parameter even if it contains commas.
        """
        # The regex splits on commas that are not inside double quotes.
        fields = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', action_input)
        # Optionally, strip extra whitespace and any surrounding quotes.
        params = [f.strip().strip('"') for f in fields]
        return params

    async def query(self, history: list, ai_client, max_turns: int = MAX_ITERATION):
        """
        Runs a multi-turn conversation with the ChatBot.
        """
        bot = ChatBot(system_prompt=self.PROMPT, history=history, ai_client=ai_client)
        try:
            for turn in range(1, max_turns + 1):
                print(f"\n--- Invocation {turn} ---")
                result = await bot.chat()
                print("Assistant:", result)

                if "Answer:" in result:
                    print("Final Answer:", result)
                    return result

                match = action_re.search(result)
                if match:
                    action, action_input = match.groups()
                    params = self.parse_parameters(action_input)

                    # Generic parameter validation using the tools dictionary.
                    if action not in self.TOOLS:
                        print(f"Error: Unknown action '{action}'.")
                        next_prompt = f"Error: Unknown action '{action}'. Please use one of the available actions."
                        history.append({"role": "user", "content": f"Observation: {next_prompt}"})
                        continue

                    required = self.TOOLS[action].get("required_params", 0)
                    if len(params) != required:
                        print(f"Error: '{action}' requires {required} parameters. Received: {params}")
                        next_prompt = f"Error: Wrong parameters for {action}. Please provide all required parameters. Example: {self.TOOLS[action]['example']}"
                        history.append({"role": "user", "content": f"Observation: {next_prompt}"})
                        continue

                    print(f" -- Running action '{action}' with input: {action_input}")
                    # self.refresh_context("test")
                    observation = await self.TOOLS[action]["function"](self, *params)
                    print("Observation:", observation)
                    history.append({"role": "user", "content": f"Observation: {observation}"})
                else:
                    print("Final Answer:", result)
                    return result
            print("Max invocation limit reached. Unable to produce a final answer.")
        finally:
            # This block executes no matter what.
            try:
                del history[bot.history_init_size]
                print(f"Removed history element at index {bot.history_init_size}.")
            except Exception as e:
                print(f"Error while removing history element at index {bot.history_init_size}: {e}")