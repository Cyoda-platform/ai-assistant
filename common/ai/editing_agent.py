import asyncio
import copy
import json
import logging
import os
import aiofiles
import httpx
from bs4 import BeautifulSoup

from common.ai.ai_agent import AiAgent
from common.ai.nltk_service import get_most_similar_entity
from common.config.config import PROJECT_DIR, REPOSITORY_NAME, ENTITY_VERSION, GOOGLE_SEARCH_KEY, GOOGLE_SEARCH_CX
from common.util.utils import _save_file, git_pull
from entity.chat.data.data_api_update import data_api_update_stack
from entity.chat.data.data_deploy import data_deploy_stack
from entity.chat.data.data_entity_add import data_entity_add_stack
from entity.chat.data.data_processors_update import data_processors_update_stack
from entity.chat.data.data_refresh_context import data_refresh_context_stack
from entity.chat.data.data_update import data_update_stack, data_answer_question
from entity.chat.data.data_workflow_add import data_workflow_add_stack
from entity.chat.data.data_workflow_update import data_workflow_update_stack
SUCCESS_MESSAGE = (
    "Work has been scheduled. You'll be notified once its done. Please exit the flow and return "
    "success message to the user immediately. Thank you!"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EditingAgent(AiAgent):
    def __init__(self, entity_service, mock=False):
        super().__init__(entity_service=entity_service, tools=self.TOOLS, mock=mock)

        self.PROMPT = f"""
            {self.PROMPT}
            
            Reason carefully about which tools to use. 
            For broad requests like adding some new functionality without specifically saying 'entity', 'workflow', 'processors', 'code' default to analyse_feature_request tool.
            if the user asks to do operations with workflow, entity, processors, api - look for a specific function first.
            Use 'minor' tools like save and read file only as supplementary.
            Most tools require chat_id: provide UUID only without any additional text
            
            If none of the tools matches the user request or it is just a general question please default to answer_general_question: chat_id, user_prompt.
            Your should always return some action, if nothing matches then default to answer_general_question: chat_id, user_prompt
            """.strip()

    def get_entities_list(self, chat_id: str) -> list:
        entity_dir = f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}/entity"

        # List all subdirectories (each subdirectory is an entity)
        entities = [name for name in os.listdir(entity_dir)
                    if os.path.isdir(os.path.join(entity_dir, name))]

        return entities

    def parse_from_string(self, escaped_code: str) -> str:
        """
        Convert a string containing escape sequences into its normal representation.

        Args:
            escaped_code: A string with literal escape characters (e.g. "\\n").

        Returns:
            A string with actual newlines and other escape sequences interpreted.
        """
        # Using the 'unicode_escape' decoding to process the escape sequences
        return escaped_code.encode("utf-8").decode("unicode_escape")

    async def web_search(self, query: str) -> str:
        """
        Performs a Google Custom Search using API key and search engine ID from environment variables.
        """
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": GOOGLE_SEARCH_KEY,
                "cx": GOOGLE_SEARCH_CX,
                "q": query,
                "num": 1  # Retrieve only the first result
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
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

    async def read_link(self, url: str) -> str:
        """
        Reads the content of a given URL and returns its textual content.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
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

    async def web_scrape(self, url: str, selector: str) -> str:
        """
        Scrapes a webpage at the given URL using the provided CSS selector and returns the extracted text.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
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

    async def save_file(self, chat_id: str, new_content: str, filename: str) -> str:
        """
        Saves data to a file using the provided chat id and file name.
        """
        try:
            new_content = self.parse_from_string(escaped_code=new_content)
            await _save_file(chat_id=chat_id, _data=new_content, item=filename)
            return "File saved successfully"
        except Exception as e:
            return f"Error during saving file: {e}"

    async def read_file(self, chat_id: str, filename: str) -> str:
        """
        Reads data from a file using the provided chat id and file name.
        """
        # Await the asynchronous git_pull function.
        await git_pull(chat_id=chat_id)

        target_dir = os.path.join(f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}", "")
        file_path = os.path.join(target_dir, filename)
        try:
            async with aiofiles.open(file_path, 'r') as file:
                content = await file.read()
            return content
        except FileNotFoundError:
            return ''
        except Exception as e:
            logger.exception("Error during reading file")
            return f"Error during reading file: {e}"

    async def _get_chat(self, chat_id: str) -> dict:
        if not self.mock:
            return await self.entity_service.get_item(
                token="cyoda_token",
                entity_model="chat",
                entity_version=ENTITY_VERSION,
                technical_id=chat_id
            )
        else:
            content = await self.read_file(chat_id=chat_id, filename="entity/chat.json")
            return json.loads(content)

    async def _update_chat(self, chat_id: str, chat: dict):
        await self.entity_service.update_item(
            token="cyoda_token",
            entity_model="chat",
            entity_version=ENTITY_VERSION,
            technical_id=chat_id,
            entity=chat,
            meta={}
        )

    def _resolve_entity_name(self, entity_name: str, chat_id: str) -> str:
        entity_names = self.get_entities_list(chat_id=chat_id)
        resolved_name = get_most_similar_entity(target=entity_name, entity_list=entity_names)
        return resolved_name if resolved_name else entity_name

    async def _execute_work_flow(self, chat_id: str, work_func) -> str:
        """
        Generic workflow executor.
        Retrieves the chat, passes its workflow stack to work_func for modifications,
        and then updates the chat.
        """
        chat = await self._get_chat(chat_id)
        stack = chat["chat_flow"]["current_flow"]
        await work_func(chat, stack)
        await self._update_chat(chat_id, chat)
        return SUCCESS_MESSAGE

    async def update_workflow(self, user_prompt: str, entity_name: str, chat_id: str) -> str:
        async def work(chat, stack):
            # Resolve entity name and read necessary files
            resolved_entity = self._resolve_entity_name(entity_name, chat_id)
            workflow_json = await self.read_file(chat_id=chat_id, filename=f"entity/{resolved_entity}/workflow.json")
            entity_model = await self.read_file(chat_id=chat_id,
                                                filename=f"entity/{resolved_entity}/{resolved_entity}.json")
            data_stack = copy.deepcopy(data_workflow_update_stack)
            stack.extend(data_stack(
                workflow_json=workflow_json,
                user_prompt=user_prompt,
                entity_model=entity_model,
                entity_name=resolved_entity
            ))

        return await self._execute_work_flow(chat_id, work)

    async def add_workflow(self, user_prompt: str, entity_name: str, chat_id: str) -> str:
        async def work(chat, stack):
            resolved_entity = self._resolve_entity_name(entity_name, chat_id)
            data_stack = copy.deepcopy(data_workflow_add_stack)
            stack.extend(data_stack(user_prompt=user_prompt, entity_name=resolved_entity))

        return await self._execute_work_flow(chat_id, work)

    async def update_processors(self, user_prompt: str, entity_name: str, chat_id: str) -> str:
        async def work(chat, stack):
            resolved_entity = self._resolve_entity_name(entity_name, chat_id)
            workflow_json = await self.read_file(chat_id=chat_id, filename=f"entity/{resolved_entity}/workflow.json")
            entity_model = await self.read_file(chat_id=chat_id,
                                                filename=f"entity/{resolved_entity}/{resolved_entity}.json")
            workflow_code = await self.read_file(chat_id=chat_id, filename=f"entity/{resolved_entity}/workflow.py")
            data_stack = copy.deepcopy(data_processors_update_stack)
            stack.extend(data_stack(
                user_prompt=user_prompt,
                entity_name=resolved_entity,
                workflow_json=workflow_json,
                entity_model=entity_model,
                workflow_code=workflow_code
            ))

        return await self._execute_work_flow(chat_id, work)

    async def add_entity(self, user_prompt: str, entity_name: str, chat_id: str) -> str:
        async def work(chat, stack):
            # Normalize entity name and update stack
            normalized_entity = entity_name.replace(" ", "_")
            data_stack = copy.deepcopy(data_entity_add_stack)
            stack.extend(data_stack(user_prompt=user_prompt, entity_name=normalized_entity))

        return await self._execute_work_flow(chat_id, work)

    async def update_api(self, user_prompt: str, entity_name: str, chat_id: str) -> str:
        async def work(chat, stack):
            normalized_entity = entity_name.replace(" ", "_")
            resolved_entity = self._resolve_entity_name(normalized_entity, chat_id)
            data_stack = copy.deepcopy(data_api_update_stack)
            stack.extend(data_stack(user_prompt=user_prompt, entity_name=resolved_entity))

        return await self._execute_work_flow(chat_id, work)

    async def analyse_feature_request(self, user_prompt: str, chat_id: str) -> str:
        async def work(chat, stack):
            # Clean up chat_id if needed
            clean_chat_id = chat_id.replace("chat_id: ", "")
            app_api = await self.read_file(chat_id=clean_chat_id, filename="app.py")
            entities_description = []
            for entity in self.get_entities_list(chat_id=clean_chat_id):
                workflow_code = await self.read_file(chat_id=clean_chat_id, filename=f"entity/{entity}/workflow.py")
                entities_description.append({entity: workflow_code})
            data_stack = copy.deepcopy(data_update_stack)
            stack.extend(data_stack(
                app_api=app_api,
                entities_description=json.dumps(entities_description),
                user_prompt=user_prompt
            ))

        return await self._execute_work_flow(chat_id, work)

    async def refresh_context(self, chat_id: str) -> str:
        async def work(chat, stack):
            data_stack = copy.deepcopy(data_refresh_context_stack)
            stack.extend(data_stack)

        return await self._execute_work_flow(chat_id, work)

    async def deploy_app(self, chat_id: str, deployment_type: str) -> str:
        async def work(chat, stack):
            data_stack = copy.deepcopy(data_deploy_stack)
            stack.extend(data_stack(deployment_type=deployment_type))

        return await self._execute_work_flow(chat_id, work)

    async def answer_general_question(self, chat_id: str, user_prompt: str) -> str:
        async def work(chat, stack):
            data_stack = copy.deepcopy(data_answer_question)
            stack.extend(data_stack(user_prompt=user_prompt))

        return await self._execute_work_flow(chat_id, work)

    # Dictionary of tools with their function, description, required parameters, and example usage.
    TOOLS = {
        "web_search": {
            "function": web_search,
            "description": "Search the web using Google Custom Search API.",
            "schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "example": 'e.g. web_search: {"query": "Python programming"}'
        },
        "read_link": {
            "function": read_link,
            "description": "Read content from a URL.",
            "schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "format": "uri"}
                },
                "required": ["url"],
                "additionalProperties": False
            },
            "example": 'e.g. read_link: {"url": "https://example.com"}'
        },
        "web_scrape": {
            "function": web_scrape,
            "description": "Scrape content from a webpage using a CSS selector.",
            "schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "format": "uri"},
                    "selector": {"type": "string"}
                },
                "required": ["url", "selector"],
                "additionalProperties": False
            },
            "example": 'e.g. web_scrape: {"url": "https://example.com", "selector": "div.article"}'
        },
        "save_file": {
            "function": save_file,
            "description": (
                "Save data to a file using the provided chat id, file contents, and file name. "
                "Ensure you provide three parameters: chat_id, new file contents, and file_name."
            ),
            "schema": {
                "type": "object",
                "properties": {
                    "chat_id": {"type": "string"},
                    "new_content": {"type": "string"},
                    "filename": {"type": "string"}
                },
                "required": ["chat_id", "new_content", "filename"],
                "additionalProperties": False
            },
            "example": 'e.g. save_file: {"chat_id": "test", "new_content": "new file contents", "filename": "filename.py"}'
        },
        "read_file": {
            "function": read_file,
            "description": "Read data from a file using chat id and file name. Use only as a utility method.",
            "schema": {
                "type": "object",
                "properties": {
                    "chat_id": {"type": "string"},
                    "filename": {"type": "string"}
                },
                "required": ["chat_id", "filename"],
                "additionalProperties": False
            },
            "example": 'e.g. read_file: {"chat_id": "test", "filename": "filename.py"}'
        },
        "update_workflow": {
            "function": update_workflow,
            "description": (
                "Update entity workflow by user prompt, entity name and chat id. Use in case user explicitly asks "
                "to make changes/update/improve/edit/etc entity {entity_name} workflow."
            ),
            "schema": {
                "type": "object",
                "properties": {
                    "user_prompt": {"type": "string"},
                    "entity_name": {"type": "string"},
                    "chat_id": {"type": "string"}
                },
                "required": ["user_prompt", "entity_name", "chat_id"],
                "additionalProperties": False
            },
            "example": 'e.g. update_workflow: {"user_prompt": "please..."", "entity_name": "some_entity", "chat_id": "please...""}'
        },
        "add_workflow": {
            "function": add_workflow,
            "description": (
                "Add entity workflow by user prompt, entity name and chat id. Use in case user explicitly asks to add "
                "workflow to entity {entity_name}. Provide complete user question as user_prompt without any modifications."
            ),
            "schema": {
                "type": "object",
                "properties": {
                    "user_prompt": {"type": "string"},
                    "entity_name": {"type": "string"},
                    "chat_id": {"type": "string"}
                },
                "required": ["user_prompt", "entity_name", "chat_id"],
                "additionalProperties": False
            },
            "example": 'e.g. add_workflow: {"user_prompt": "please..."", "entity_name": "some_entity", "chat_id": "test"}'
        },
        "update_processors": {
            "function": update_processors,
            "description": (
                "Add/update existing processors (workflow code) for entity workflow by user prompt, entity name and chat id. "
                "Use in case user asks to add processors code for entity {entity_name} workflow. Provide complete user question "
                "as user_prompt without any modifications."
            ),
            "schema": {
                "type": "object",
                "properties": {
                    "user_prompt": {"type": "string"},
                    "entity_name": {"type": "string"},
                    "chat_id": {"type": "string"}
                },
                "required": ["user_prompt", "entity_name", "chat_id"],
                "additionalProperties": False
            },
            "example": 'e.g. update_processors: {"user_prompt": "please..."", "entity_name": "some_entity", "chat_id": "test"}'
        },
        "add_entity": {
            "function": add_entity,
            "description": (
                "Add a new entity with {entity_name} specified by the user. Provide complete user question as user_prompt "
                "without any modifications."
            ),
            "schema": {
                "type": "object",
                "properties": {
                    "user_prompt": {"type": "string"},
                    "entity_name": {"type": "string"},
                    "chat_id": {"type": "string"}
                },
                "required": ["user_prompt", "entity_name", "chat_id"],
                "additionalProperties": False
            },
            "example": 'e.g. add_entity: {"user_prompt": "please..."", "entity_name": "some_entity", "chat_id": "test"}'
        },
        "update_api": {
            "function": update_api,
            "description": (
                "Update API according to the user requirement. Use this function to add new endpoints to app.py. Provide complete "
                "user question as user_prompt without any modifications."
            ),
            "schema": {
                "type": "object",
                "properties": {
                    "user_prompt": {"type": "string"},
                    "entity_name": {"type": "string"},
                    "chat_id": {"type": "string"}
                },
                "required": ["user_prompt", "entity_name", "chat_id"],
                "additionalProperties": False
            },
            "example": 'e.g. update_api: {"user_prompt": "please..."", "entity_name": "some_entity", "chat_id": "test"}'
        },
        "analyse_feature_request": {
            "function": analyse_feature_request,
            "description": (
                "Analyse user feature request and return execution plan. Use this action if the user requirement is broad and is not "
                "limited to the scope of other actions. Provide complete user question as user_prompt without any modifications."
            ),
            "schema": {
                "type": "object",
                "properties": {
                    "user_prompt": {"type": "string"},
                    "chat_id": {"type": "string"}
                },
                "required": ["user_prompt", "chat_id"],
                "additionalProperties": False
            },
            "example": 'e.g. analyse_feature_request: {"user_prompt": "please..."", "chat_id": "test"}'
        },
        "refresh_context": {
            "function": refresh_context,
            "description": "Use this action if the user wants to clear the chat/refresh chat context/clear the session history.",
            "schema": {
                "type": "object",
                "properties": {
                    "chat_id": {"type": "string"}
                },
                "required": ["chat_id"],
                "additionalProperties": False
            },
            "example": 'e.g. refresh_context: {"chat_id": "test"}'
        },
        "deploy_app": {
            "function": deploy_app,
            "description": (
                "Use this action if the user wants to deploy cyoda environment or their application. Choose deployment_type value "
                "from [\"cyoda_env\", \"user_app\"]. Choose cyoda_env only if the user explicitly asks for cyoda environment; "
                "otherwise default to user_app."
            ),
            "schema": {
                "type": "object",
                "properties": {
                    "chat_id": {"type": "string"},
                    "deployment_type": {"type": "string", "enum": ["cyoda_env", "user_app"]}
                },
                "required": ["chat_id", "deployment_type"],
                "additionalProperties": False
            },
            "example": 'e.g. deploy_app: {"chat_id": "chat_id", "deployment_type": "user_app"}'
        },
        "answer_general_question": {
            "function": answer_general_question,
            "description": (
                "Use this action to answer random questions that do not match any other tool. Use it as a last option if nothing else matches."
            ),
            "schema": {
                "type": "object",
                "properties": {
                    "chat_id": {"type": "string"},
                    "user_prompt": {"type": "string"}
                },
                "required": ["chat_id", "user_prompt"],
                "additionalProperties": False
            },
            "example": 'e.g. answer_general_question: {"chat_id": "test", "user_prompt": "please..."}'
        }
    }


def main():
    # Example invocation for fixing the app.py file.
    from common.repository.in_memory_db import InMemoryRepository
    from common.service.service import EntityServiceImpl

    editing_agent = EditingAgent(entity_service=EntityServiceImpl(InMemoryRepository()), mock=True)
    #ai_question = """please add processor code for posts entity workflow, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    #ai_question = """please add new entity for posts, get the model at https://jsonplaceholder.typicode.com/posts/1, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    #ai_question = """please add new api for posts to get data from https://jsonplaceholder.typicode.com/posts/1, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    #ai_question = """please add new GET endpoint for posts to get data from https://jsonplaceholder.typicode.com/posts/1, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    #ai_question = """please add a new data source that gets data from https://jsonplaceholder.typicode.com/posts/1, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    #ai_question = """please add a new data source that gets data from https://jsonplaceholder.typicode.com/posts/1, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    ai_question = """please clear the chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""

    history = [{"role": "system", "content": editing_agent.PROMPT},
               {"role": "user", "content": ai_question}]
    from openai import AsyncOpenAI
    asyncio.run(editing_agent.query(history=history, ai_client=AsyncOpenAI()))


if __name__ == "__main__":
    main()
