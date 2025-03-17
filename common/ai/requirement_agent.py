import asyncio
import logging
import os
import re
import httpx
from bs4 import BeautifulSoup
import aiofiles

from common.ai.ai_agent import AiAgent
from common.config.config import GOOGLE_SEARCH_KEY, GOOGLE_SEARCH_CX, PROJECT_DIR, REPOSITORY_NAME
from common.util.utils import _save_file, git_pull

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Regular expression to parse action lines from the assistant output.
action_re = re.compile(r'^Action: (\w+): (.+)$', re.MULTILINE)
collected_docs = []


class RequirementAgent(AiAgent):
    def __init__(self):
        super().__init__(tools=self.TOOLS)

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

    async def save_file(self, chat_id: str, data: str, file_name: str) -> str:
        """
        Saves data to a file using the provided chat id and file name.
        """
        try:
            data = self.parse_from_string(escaped_code=data)
            await _save_file(chat_id=chat_id, _data=data, item=file_name)
            return "File saved successfully"
        except Exception as e:
            return f"Error during saving file: {e}"

    async def read_file(self, chat_id: str, file_name: str) -> str:
        """
        Reads data from a file using the provided chat id and file name.
        """
        # Await the asynchronous git_pull function.
        await git_pull(chat_id=chat_id)

        target_dir = os.path.join(f"{PROJECT_DIR}/{chat_id}/{REPOSITORY_NAME}", "")
        file_path = os.path.join(target_dir, file_name)
        try:
            async with aiofiles.open(file_path, 'r') as file:
                content = await file.read()
            return content
        except FileNotFoundError:
            return ''
        except Exception as e:
            logger.exception("Error during reading file")
            return f"Error during reading file: {e}"

    # Dictionary of tools with their function, description, required parameters, and example usage.
    TOOLS = {
        "web_search": {
            "function": web_search,
            "description": "Search the web using Google Custom Search API.  Use this function when you need to formulate the questions/requirement for information that should be searched online. For example, the user wants to add dat asources for example api, but does not provide exact link or documentation",
            "required_params": 1,
            "example": "e.g. web_search: Python programming"
        },
        "read_link": {
            "function": read_link,
            "description": "Read content from a URL. Use this function when you need to formulate the questions/requirement for information that should be fetched from a web resource. For example, the user wants to add data sources for example api and provides exact link. You should first read the link contents and only after that proceed to analysing the user question.",
            "required_params": 1,
            "example": "e.g. read_link: https://example.com"
        },
        "web_scrape": {
            "function": web_scrape,
            "description": "Scrape content from a webpage using a CSS selector. Use this function when you need to formulate the questions/requirement for information that should be web scraped online. For example, the user wants to add data sources for example api and provides exact link to do web scraping. You should first web scrape the resource and only after that proceed to analysing the user question.",
            "required_params": 2,
            "example": "e.g. web_scrape: https://example.com, div.article"
        }
        # "save_file": {
        #     "function": save_file,
        #     "description": ("Save data to a file using the provided chat id, file contents, and file name. "
        #                     "Ensure you provide three parameters: chat_id, new file contents, and file_name."),
        #     "required_params": 3,
        #     "example": "e.g. save_file: chat_id, \"new file contents\", filename.py"
        # },
        # "read_file": {
        #     "function": read_file,
        #     "description": "Read data from a file using chat id and file name. Use only as a utility method.",
        #     "required_params": 2,
        #     "example": "e.g. read_file: chat_id, filename.py"
        # }
    }


def main():
    # Example invocation for fixing the app.py file.
    from common.repository.in_memory_db import InMemoryRepository
    from common.service.service import EntityServiceImpl

    requirement_agent = RequirementAgent()
    # ai_question = """please add processor code for posts entity workflow, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    # ai_question = """please add new entity for posts, get the model at https://jsonplaceholder.typicode.com/posts/1, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    # ai_question = """please add new api for posts to get data from https://jsonplaceholder.typicode.com/posts/1, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    # ai_question = """please add new GET endpoint for posts to get data from https://jsonplaceholder.typicode.com/posts/1, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    # ai_question = """please add a new data source that gets data from https://jsonplaceholder.typicode.com/posts/1, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    # ai_question = """please add a new data source that gets data from https://jsonplaceholder.typicode.com/posts/1, chat id = 69f55092-fda7-11ef-a082-40c2ba0ac9eb"""
    ai_question = """please search for the Washington's middle name"""

    history = [{"role": "system", "content": requirement_agent.PROMPT},
               {"role": "user", "content": ai_question}]
    from openai import AsyncOpenAI
    asyncio.run(requirement_agent.query(history=history, ai_client=AsyncOpenAI()))


if __name__ == "__main__":
    main()