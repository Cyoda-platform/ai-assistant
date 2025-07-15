import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tools.web_operations_service import WebOperationsService
from entity.chat.chat import ChatEntity


class TestWebOperationsService:
    """Test cases for WebOperationsService."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for WebOperationsService."""
        return {
            'workflow_helper_service': AsyncMock(),
            'entity_service': AsyncMock(),
            'cyoda_auth_service': MagicMock(),
            'workflow_converter_service': AsyncMock(),
            'scheduler_service': AsyncMock(),
            'data_service': AsyncMock(),
        }

    @pytest.fixture
    def service(self, mock_dependencies):
        """Create WebOperationsService instance."""
        return WebOperationsService(**mock_dependencies)

    @pytest.fixture
    def mock_chat_entity(self):
        """Create mock ChatEntity."""
        entity = MagicMock(spec=ChatEntity)
        entity.failed = False
        entity.error = None
        return entity

    @pytest.mark.asyncio
    async def test_web_search_success(self, service, mock_chat_entity):
        """Test successful web search."""
        # Mock the httpx.AsyncClient to return a successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "snippet": "Search results for test query"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await service.web_search("tech_id", mock_chat_entity, query="test query")

            assert result == "Search results for test query"

    @pytest.mark.asyncio
    async def test_web_search_missing_query(self, service, mock_chat_entity):
        """Test web search with missing query."""
        result = await service.web_search("tech_id", mock_chat_entity)
        
        assert "Missing required parameters: query" in result

    @pytest.mark.asyncio
    async def test_web_search_error(self, service, mock_chat_entity):
        """Test web search with error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Search error")

            result = await service.web_search("tech_id", mock_chat_entity, query="test")

            assert "Error during search" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_read_link_success(self, service, mock_chat_entity):
        """Test successful link reading."""
        # Mock the httpx.AsyncClient to return HTML content
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Link content</p></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await service.read_link("tech_id", mock_chat_entity, url="https://example.com")

            assert "Link content" in result

    @pytest.mark.asyncio
    async def test_read_link_missing_url(self, service, mock_chat_entity):
        """Test link reading with missing URL."""
        result = await service.read_link("tech_id", mock_chat_entity)
        
        assert "Missing required parameters: url" in result

    @pytest.mark.asyncio
    async def test_read_link_error(self, service, mock_chat_entity):
        """Test link reading with error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Read error")

            result = await service.read_link("tech_id", mock_chat_entity, url="https://example.com")

            assert "Sorry, there were issues while doing your task. Please retry." in result

    @pytest.mark.asyncio
    async def test_web_scrape_success(self, service, mock_chat_entity):
        """Test successful web scraping."""
        # Mock the httpx.AsyncClient to return HTML content
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Scraped content</p><div>Other content</div></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await service.web_scrape("tech_id", mock_chat_entity, url="https://example.com", selector="p")

            assert "Scraped content" in result

    @pytest.mark.asyncio
    async def test_web_scrape_missing_url(self, service, mock_chat_entity):
        """Test web scraping with missing URL."""
        result = await service.web_scrape("tech_id", mock_chat_entity)

        assert "Missing required parameters: url, selector" in result

    @pytest.mark.asyncio
    async def test_web_scrape_error(self, service, mock_chat_entity):
        """Test web scraping with error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Scrape error")

            result = await service.web_scrape("tech_id", mock_chat_entity, url="https://example.com", selector="p")

            assert "Error during web scraping" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_get_cyoda_guidelines_success(self, service, mock_chat_entity):
        """Test successful Cyoda guidelines retrieval."""
        # Mock the httpx.AsyncClient to return guidelines content
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Cyoda guidelines content</p></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await service.get_cyoda_guidelines("tech_id", mock_chat_entity, workflow_name="test_workflow")

            assert "Cyoda guidelines content" in result

    @pytest.mark.asyncio
    async def test_get_cyoda_guidelines_error(self, service, mock_chat_entity):
        """Test Cyoda guidelines retrieval with error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Guidelines error")

            result = await service.get_cyoda_guidelines("tech_id", mock_chat_entity, workflow_name="test_workflow")

            assert "Sorry, there were issues while doing your task. Please retry." in result

    @pytest.mark.asyncio
    async def test_web_search_with_custom_params(self, service, mock_chat_entity):
        """Test web search with custom parameters."""
        # Mock the httpx.AsyncClient to return search results
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "snippet": "Custom search results"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await service.web_search(
                "tech_id", mock_chat_entity,
                query="test query",
                max_results=10,
                custom_param="value"
            )

            assert result == "Custom search results"

    @pytest.mark.asyncio
    async def test_read_link_with_custom_params(self, service, mock_chat_entity):
        """Test link reading with custom parameters."""
        # Mock the httpx.AsyncClient to return HTML content
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Custom link content</p></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await service.read_link(
                "tech_id", mock_chat_entity,
                url="https://example.com",
                timeout=30,
                headers={"User-Agent": "test"}
            )

            assert "Custom link content" in result

    @pytest.mark.asyncio
    async def test_web_scrape_with_custom_params(self, service, mock_chat_entity):
        """Test web scraping with custom parameters."""
        # Mock the httpx.AsyncClient to return HTML content
        mock_response = MagicMock()
        mock_response.text = "<html><body><div class='content'>Custom scraped content</div></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await service.web_scrape(
                "tech_id", mock_chat_entity,
                url="https://example.com",
                selector=".content",
                wait_time=5
            )

            assert "Custom scraped content" in result

    @pytest.mark.asyncio
    async def test_get_cyoda_guidelines_with_custom_params(self, service, mock_chat_entity):
        """Test Cyoda guidelines retrieval with custom parameters."""
        # Mock the httpx.AsyncClient to return guidelines content
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Custom guidelines content</p></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await service.get_cyoda_guidelines(
                "tech_id", mock_chat_entity,
                workflow_name="test_workflow",
                section="api",
                version="v2"
            )

            assert "Custom guidelines content" in result

    def test_service_inheritance(self, service):
        """Test that service properly inherits from BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        assert isinstance(service, BaseWorkflowService)
        assert hasattr(service, 'logger')
        assert hasattr(service, '_handle_error')
        assert hasattr(service, '_validate_required_params')
