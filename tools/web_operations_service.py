import httpx
from bs4 import BeautifulSoup

from common.config.config import config
from entity.chat.chat import ChatEntity
from tools.base_service import BaseWorkflowService


class WebOperationsService(BaseWorkflowService):
    """
    Service responsible for all web-related operations including
    web searching, link reading, web scraping, and HTTP requests.
    """

    async def web_search(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Performs a Google Custom Search using API key and search engine ID from environment variables.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including query
            
        Returns:
            Search result snippet or error message
        """
        try:
            is_valid, error_msg = await self._validate_required_params(params, ["query"])
            if not is_valid:
                return error_msg

            url = "https://www.googleapis.com/customsearch/v1"
            search_params = {
                "key": config.GOOGLE_SEARCH_KEY,
                "cx": config.GOOGLE_SEARCH_CX,
                "q": params.get("query"),
                "num": 1  # Retrieve only the first result
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=search_params)
            response.raise_for_status()
            
            data = response.json()
            if "items" in data and data["items"]:
                first_item = data["items"][0]
                snippet = first_item.get("snippet")
                result = snippet if snippet else "No snippet available."
            else:
                result = "No results found."
                
            return result
            
        except Exception as e:
            return self._handle_error(entity, e, f"Error during search: {e}")

    async def read_link(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Reads the content of a given URL and returns its textual content.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including url
            
        Returns:
            URL content or error message
        """
        try:
            is_valid, error_msg = await self._validate_required_params(params, ["url"])
            if not is_valid:
                return error_msg
                
            return await self._fetch_data(url=params.get("url"))
            
        except Exception as e:
            return self._handle_error(entity, e, f"Error reading link: {e}")

    async def web_scrape(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Scrapes a webpage at the given URL using the provided CSS selector and returns the extracted text.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including url and selector
            
        Returns:
            Scraped content or error message
        """
        try:
            is_valid, error_msg = await self._validate_required_params(params, ["url", "selector"])
            if not is_valid:
                return error_msg

            async with httpx.AsyncClient() as client:
                response = await client.get(params.get("url"))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.select(params.get("selector"))
            
            if elements:
                content = "\n".join(element.get_text(separator=" ", strip=True) for element in elements)
                result = content
            else:
                result = "No elements found for the given selector."
                
            return result
            
        except Exception as e:
            return self._handle_error(entity, e, f"Error during web scraping: {e}")

    async def _fetch_data(self, url: str) -> str:
        """
        Internal method to fetch and parse data from a URL.
        
        Args:
            url: URL to fetch data from
            
        Returns:
            Parsed text content from the URL
            
        Raises:
            Exception: If there are issues fetching or parsing the data
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
                
            return result
            
        except Exception as e:
            self.logger.exception(e)
            return "Sorry, there were issues while doing your task. Please retry."

    async def get_cyoda_guidelines(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Retrieve Cyoda guidelines for a specific workflow.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including workflow_name
            
        Returns:
            Guidelines content or error message
        """
        try:
            is_valid, error_msg = await self._validate_required_params(params, ["workflow_name"])
            if not is_valid:
                return error_msg
                
            url = f"{config.DATA_REPOSITORY_URL}/get_cyoda_guidelines/{params.get('workflow_name')}.adoc"
            return await self._fetch_data(url=url)
            
        except Exception as e:
            return self._handle_error(entity, e, f"Error fetching Cyoda guidelines: {e}")
