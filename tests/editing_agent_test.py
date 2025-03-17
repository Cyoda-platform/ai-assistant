import asyncio
import json
import logging
import os
import re

import httpx
from bs4 import BeautifulSoup
from openai import OpenAI

from common.ai.nltk_service import get_most_similar_entity
from common.config.config import PROJECT_DIR, REPOSITORY_NAME
from common.util.utils import _save_file, git_pull
from entity.chat.data.data_api_update import data_api_update_stack
from entity.chat.data.data_entity_add import data_entity_add_stack
from entity.chat.data.data_processors_update import data_processors_update_stack
from entity.chat.data.data_refresh_context import data_refresh_context_stack
from entity.chat.data.data_update import data_update_stack
from entity.chat.data.data_workflow_add import data_workflow_add_stack
from entity.chat.data.data_workflow_update import data_workflow_update_stack
from entity.chat.workflow.logic import mock_process_dialogue_script
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Regular expression to parse action lines from the assistant output.
action_re = re.compile(r'^Action: (\w+): (.+)$', re.MULTILINE)


def get_entities_list(chat_id: str) -> list:
    entity_dir = f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}/entity"

    # List all subdirectories (each subdirectory is an entity)
    entities = [name for name in os.listdir(entity_dir)
                if os.path.isdir(os.path.join(entity_dir, name))]

    return entities


def parse_from_string(escaped_code: str) -> str:
    """
    Convert a string containing escape sequences into its normal representation.

    Args:
        escaped_code: A string with literal escape characters (e.g. "\\n").

    Returns:
        A string with actual newlines and other escape sequences interpreted.
    """
    # Using the 'unicode_escape' decoding to process the escape sequences
    return escaped_code.encode("utf-8").decode("unicode_escape")


def parse_parameters(action_input: str) -> list:
    """
    Splits the action input into parameters, treating text wrapped in double quotes
    as a single parameter even if it contains commas.
    """
    # The regex splits on commas that are not inside double quotes.
    fields = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', action_input)
    # Optionally, strip extra whitespace and any surrounding quotes.
    params = [f.strip().strip('"') for f in fields]
    return params


def web_search(query: str) -> str:
    """
    Performs a Google Custom Search using API key and search engine ID from environment variables.
    """
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": "AIzaSyCfgshhWHeW4NvIM2AqwQQtF27IiOnHn_A",
            "cx": "87ab6273b091a481e",
            "q": query,
            "num": 1  # Retrieve only the first result
        }
        response = httpx.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "items" in data and data["items"]:
            first_item = data["items"][0]
            snippet = first_item.get("snippet")
            result = snippet if snippet else "No snippet available."
        else:
            result = "No results found."
    except Exception as e:
        result = f"Error during search: {e}"
    return result


def read_link(url: str) -> str:
    """
    Reads the content of a given URL and returns its textual content.
    """
    try:
        response = httpx.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        if paragraphs:
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            result = content
        else:
            result = soup.get_text(strip=True)
    except Exception as e:
        result = f"Error reading link: {e}"
    return result


def web_scrape(url: str, selector: str) -> str:
    """
    Scrapes a webpage at the given URL using the provided CSS selector and returns the extracted text.
    """
    try:
        response = httpx.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        elements = soup.select(selector)
        if elements:
            content = "\n".join(element.get_text(separator=" ", strip=True) for element in elements)
            result = content
        else:
            result = "No elements found for the given selector."
    except Exception as e:
        result = f"Error during web scraping: {e}"
    return result


def save_file(chat_id: str, data: str, file_name: str) -> str:
    """
    Saves data to a file using the provided chat id and file name.
    """
    try:
        data = parse_from_string(data)
        asyncio.run(_save_file(chat_id=chat_id, _data=data, item=file_name))
        return "File saved successfully"
    except Exception as e:
        return f"Error during saving file: {e}"


def read_file(chat_id: str, file_name: str) -> str:
    """
    Reads data from a file using the provided chat id and file name.
    """
    asyncio.run(git_pull(chat_id=chat_id))
    target_dir = os.path.join(f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}", "")
    file_path = os.path.join(target_dir, file_name)
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    except Exception as e:
        logger.exception("Error during reading file")
        return f"Error during reading file: {e}"


def update_workflow(user_prompt: str, entity_name: str, chat_id: str) -> str:
    chat = json.loads(read_file(chat_id=chat_id, file_name=f"entity/chat.json"))
    stack = chat["chat_flow"]["current_flow"]
    entity_names = get_entities_list(chat_id=chat_id)
    entity_name = get_most_similar_entity(target=entity_name, entity_list=entity_names)
    workflow_json = read_file(chat_id=chat_id, file_name=f"entity/{entity_name}/workflow.json")
    entity_model = read_file(chat_id=chat_id, file_name=f"entity/{entity_name}/{entity_name}.json")
    stack.extend(data_workflow_update_stack(workflow_json=workflow_json,
                                            user_prompt=user_prompt,
                                            entity_model=entity_model,
                                            entity_name=entity_name))
    asyncio.run(mock_process_dialogue_script(chat=chat))
    return f"{user_prompt} has been successfully done. Please exit the flow and return success message to the user immediately. Thank you!"


def add_workflow(user_prompt: str, entity_name: str, chat_id: str) -> str:
    chat = json.loads(read_file(chat_id=chat_id, file_name=f"entity/chat.json"))
    stack = chat["chat_flow"]["current_flow"]
    entity_names = get_entities_list(chat_id=chat_id)
    existing_entity_name = get_most_similar_entity(target=entity_name, entity_list=entity_names)
    entity_name = existing_entity_name if existing_entity_name else entity_name
    stack.extend(data_workflow_add_stack(user_prompt=user_prompt, entity_name=entity_name))
    asyncio.run(mock_process_dialogue_script(chat=chat))
    return f"{user_prompt} has been successfully done. Please exit the flow and return success message to the user immediately. Thank you!"


def update_processors(user_prompt: str, entity_name: str, chat_id: str) -> str:
    chat = json.loads(read_file(chat_id=chat_id, file_name=f"entity/chat.json"))
    stack = chat["chat_flow"]["current_flow"]
    entity_names = get_entities_list(chat_id=chat_id)
    existing_entity_name = get_most_similar_entity(target=entity_name, entity_list=entity_names)
    entity_name = existing_entity_name if existing_entity_name else entity_name
    workflow_json = read_file(chat_id=chat_id, file_name=f"entity/{entity_name}/workflow.json")
    entity_model = read_file(chat_id=chat_id, file_name=f"entity/{entity_name}/{entity_name}.json")
    workflow_code = read_file(chat_id=chat_id, file_name=f"entity/{entity_name}/workflow.py")
    stack.extend(
        data_processors_update_stack(user_prompt=user_prompt, entity_name=entity_name, workflow_json=workflow_json,
                                     entity_model=entity_model, workflow_code=workflow_code))
    asyncio.run(mock_process_dialogue_script(chat=chat))
    return f"{user_prompt} has been successfully done. Please exit the flow and return success message to the user immediately. Thank you!"

def add_entity(user_prompt: str, entity_name: str, chat_id: str) -> str:
    chat = json.loads(read_file(chat_id=chat_id, file_name=f"entity/chat.json"))
    stack = chat["chat_flow"]["current_flow"]
    entity_name.replace(" ", "_")
    stack.extend(data_entity_add_stack(user_prompt=user_prompt, entity_name=entity_name))
    asyncio.run(mock_process_dialogue_script(chat=chat))
    return f"""Entity {entity_name} has been saved successfully.
user_has_provided_workflow_description = evaluate {user_prompt} if user has provided workflow information.
if user_has_provided_workflow_description == true, then next 'Action: add_workflow: {user_prompt}, {entity_name}, {chat_id}' else exit immediately"""

def update_api(user_prompt: str, entity_name: str, chat_id: str) -> str:
    chat = json.loads(read_file(chat_id=chat_id, file_name=f"entity/chat.json"))
    stack = chat["chat_flow"]["current_flow"]
    entity_name.replace(" ", "_")
    entity_names = get_entities_list(chat_id=chat_id)
    existing_entity_name = get_most_similar_entity(target=entity_name, entity_list=entity_names)
    entity_name = existing_entity_name if existing_entity_name else entity_name
    stack.extend(data_api_update_stack(user_prompt=user_prompt, entity_name=entity_name))
    asyncio.run(mock_process_dialogue_script(chat=chat))
    return f"""API updated successfully, please, exit immediately"""

def analyse_feature_request(user_prompt: str, chat_id: str) -> str:
    chat = json.loads(read_file(chat_id=chat_id, file_name=f"entity/chat.json"))
    stack = chat["chat_flow"]["current_flow"]
    app_api = read_file(chat_id=chat_id, file_name=f"app.py")
    entities_description = []
    entity_names = get_entities_list(chat_id=chat_id)
    for entity_name in entity_names:
        workflow_code = read_file(chat_id=chat_id, file_name=f"entity/{entity_name}/workflow.py")
        entities_description.append({entity_name: workflow_code})
    stack.extend(data_update_stack(app_api=app_api, entities_description=json.dumps(entities_description), user_prompt=user_prompt))
    asyncio.run(mock_process_dialogue_script(chat=chat))
    return f"""Analysis complete"""

def refresh_context(chat_id: str) -> str:
    chat = json.loads(read_file(chat_id=chat_id, file_name=f"entity/chat.json"))
    stack = chat["chat_flow"]["current_flow"]
    stack.extend(data_refresh_context_stack)
    asyncio.run(mock_process_dialogue_script(chat=chat))
    return f"""Context refresh complete"""

# Dictionary of tools with their function, description, required parameters, and example usage.
TOOLS = {
    "web_search": {
        "function": web_search,
        "description": "Search the web using Google Custom Search API.",
        "required_params": 1,
        "example": "e.g. web_search: Python programming"
    },
    "read_link": {
        "function": read_link,
        "description": "Read content from a URL.",
        "required_params": 1,
        "example": "e.g. read_link: https://example.com"
    },
    "web_scrape": {
        "function": web_scrape,
        "description": "Scrape content from a webpage using a CSS selector.",
        "required_params": 2,
        "example": "e.g. web_scrape: https://example.com, div.article"
    },
    "save_file": {
        "function": save_file,
        "description": ("Save data to a file using the provided chat id, file contents, and file name. "
                        "Ensure you provide three parameters: chat_id, new file contents, and file_name."),
        "required_params": 3,
        "example": "e.g. save_file: chat_id, \"new file contents\", filename.py"
    },
    "read_file": {
        "function": read_file,
        "description": "Read data from a file using chat id and file name.",
        "required_params": 2,
        "example": "e.g. read_file: chat_id, filename.py"
    },
    "update_workflow": {
        "function": update_workflow,
        "description": "Update entity workflow by user prompt, entity name and chat id. Use in case user explicitly asks to make changes/update/improve/edit/etc entity {entity_name} workflow",
        "required_params": 3,
        "example": "e.g. update_workflow: user_prompt, entity_name, chat_id"
    },
    "add_workflow": {
        "function": add_workflow,
        "description": "Add entity workflow by user prompt, entity name and chat id. Use in case user explicitly asks to add workflow to entity {entity_name}. Here the user requires adding workflow configuration generation, not code. Provide complete user question as user_prompt without any modifications.",
        "required_params": 3,
        "example": "e.g. add_workflow: user_prompt, entity_name, chat_id"
    },
    "update_processors": {
        "function": update_processors,
        "description": "Add/update existing processors (workflow code) for entity workflow by user prompt, entity name and chat id. Use in case user asks to add processors code for to entity {entity_name} workflow. Here the user requires code generation. Key words: processors, code. Provide complete user question as user_prompt without any modifications.",
        "required_params": 3,
        "example": "e.g. update_processors: user_prompt, entity_name, chat_id"
    },
    "add_entity": {
        "function": add_entity,
        "description": "Add a new entity with {entity_name} specified by the user. Provide complete user question as user_prompt without any modifications.",
        "required_params": 3,
        "example": "e.g. add_entity: user_prompt, entity_name, chat_id"
    },
    "update_api": {
        "function": update_api,
        "description": "Update api according to the user requirement. Use this function to add new endpoints to app.py. Provide complete user question as user_prompt without any modifications.",
        "required_params": 3,
        "example": "e.g. update_api: user_prompt, entity_name, chat_id"
    },
    "analyse_feature_request": {
        "function": analyse_feature_request,
        "description": "Analyse user feature request and return execution plan. Example usage: user wants to add a new feature like a introducing a new datasource, additional service or edit the existing logic. Use this action if the user requirement is broad and is not limited to the scope of other actions. Provide complete user question as user_prompt without any modifications.",
        "required_params": 2,
        "example": "e.g. analyse_feature_request: user_prompt, chat_id"
    },
    "refresh_context": {
        "function": refresh_context,
        "description": "Use this action if the user wants to clear the chat/refresh chat context/clear the session history",
        "required_params": 1,
        "example": "e.g. refresh_context: chat_id"
    }
}



def get_tools_description() -> str:
    """
    Generates a dynamic description for each tool.
    """
    descriptions = []
    for name, tool in TOOLS.items():
        descriptions.append(f"{name}: {tool['description']} {tool['example']}")
    return "\n".join(descriptions)


TOOLS_DESCRIPTION = get_tools_description()

# Enhanced prompt with detailed instructions and examples.
PROMPT = f"""
You are a highly knowledgeable assistant specialized in code analysis, debugging, and repository management. 
You operate using a Thought-Action-Observation loop to analyze issues and apply fixes iteratively.

Guidelines:
1. Begin your response with "Thought:" to explain your reasoning.
2. If you need to perform an action (such as reading a file, searching the web, scraping content, or saving changes), output exactly one line in the format:
   "Action: <tool_name>: <input parameters>"
   For example: "Action: read_file: chat_id, filename.py"
3. For the "save_file" action, you must always include three comma-separated parameters: chat_id, new file contents (in quotes if necessary), and file_name.
4. Wait for an "Observation:" response before proceeding to further reasoning or actions.
5. If you can directly provide the final answer, begin your response with "Answer:" followed by your answer.
6. Always end your final answer with "Answer:" followed by the resolved result or explanation.

Available Tools:
{TOOLS_DESCRIPTION}

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


class ChatBot:
    """
    ChatBot that maintains conversation history and interacts with the OpenAI API.
    """

    def __init__(self, system_prompt, history):
        self.client = OpenAI()  # Ensure your OpenAI API key is properly configured
        self.history = history
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})
        else:
            self.history.append({"role": "system", "content": PROMPT})

    def chat(self) -> str:
        """
        Appends the user message to history, calls the API, appends the response, and returns it.
        """
        result = self._execute()
        self.history.append({"role": "assistant", "content": result})
        return result

    def _execute(self) -> str:
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
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


def query(history: list, max_turns: int = 3):
    """
    Runs a multi-turn conversation with the ChatBot.
    """
    bot = ChatBot(system_prompt=PROMPT, history=history)
    for turn in range(1, max_turns + 1):
        print(f"\n--- Invocation {turn} ---")
        result = bot.chat()
        print("Assistant:", result)

        if "Answer:" in result:
            print("Final Answer:", result)
            return result

        match = action_re.search(result)
        if match:
            action, action_input = match.groups()
            params = parse_parameters(action_input)

            # Generic parameter validation using the tools dictionary.
            if action not in TOOLS:
                print(f"Error: Unknown action '{action}'.")
                next_prompt = f"Error: Unknown action '{action}'. Please use one of the available actions."
                continue

            required = TOOLS[action].get("required_params", 0)
            if len(params) != required:
                print(f"Error: '{action}' requires {required} parameters. Received: {params}")
                next_prompt = f"Error: Wrong parameters for {action}. Please provide all required parameters. Example: {TOOLS[action]['example']}"
                continue

            print(f" -- Running action '{action}' with input: {action_input}")
            observation = TOOLS[action]["function"](*params)
            print("Observation:", observation)
            history.append({"role": "user", "content": f"Observation: {observation}"})
        else:
            print("Final Answer:", result)
            return result
    print("Max invocation limit reached. Unable to produce a final answer.")


def main():
    # Example invocation for fixing the app.py file.
    ai_question = """please clear the chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    history = [{"role": "system", "content": PROMPT},
               {"role": "user", "content": ai_question}]
    query(history=history)


if __name__ == "__main__":
    main()
