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
        with patch('common.utils.web_search.web_search', new_callable=AsyncMock, 
                  return_value="Search results for test query") as mock_search:
            
            result = await service.web_search("tech_id", mock_chat_entity, query="test query")
            
            assert result == "Search results for test query"
            mock_search.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_web_search_missing_query(self, service, mock_chat_entity):
        """Test web search with missing query."""
        result = await service.web_search("tech_id", mock_chat_entity)
        
        assert "Missing required parameters: query" in result

    @pytest.mark.asyncio
    async def test_web_search_error(self, service, mock_chat_entity):
        """Test web search with error."""
        with patch('common.utils.web_search.web_search', new_callable=AsyncMock, 
                  side_effect=Exception("Search error")):
            
            result = await service.web_search("tech_id", mock_chat_entity, query="test")
            
            assert "Error during web search" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_read_link_success(self, service, mock_chat_entity):
        """Test successful link reading."""
        with patch('common.utils.web_search.read_link', new_callable=AsyncMock, 
                  return_value="Link content") as mock_read:
            
            result = await service.read_link("tech_id", mock_chat_entity, url="https://example.com")
            
            assert result == "Link content"
            mock_read.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_read_link_missing_url(self, service, mock_chat_entity):
        """Test link reading with missing URL."""
        result = await service.read_link("tech_id", mock_chat_entity)
        
        assert "Missing required parameters: url" in result

    @pytest.mark.asyncio
    async def test_read_link_error(self, service, mock_chat_entity):
        """Test link reading with error."""
        with patch('common.utils.web_search.read_link', new_callable=AsyncMock, 
                  side_effect=Exception("Read error")):
            
            result = await service.read_link("tech_id", mock_chat_entity, url="https://example.com")
            
            assert "Error reading link" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_web_scrape_success(self, service, mock_chat_entity):
        """Test successful web scraping."""
        with patch('common.utils.web_search.web_scrape', new_callable=AsyncMock, 
                  return_value="Scraped content") as mock_scrape:
            
            result = await service.web_scrape("tech_id", mock_chat_entity, url="https://example.com")
            
            assert result == "Scraped content"
            mock_scrape.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_web_scrape_missing_url(self, service, mock_chat_entity):
        """Test web scraping with missing URL."""
        result = await service.web_scrape("tech_id", mock_chat_entity)
        
        assert "Missing required parameters: url" in result

    @pytest.mark.asyncio
    async def test_web_scrape_error(self, service, mock_chat_entity):
        """Test web scraping with error."""
        with patch('common.utils.web_search.web_scrape', new_callable=AsyncMock, 
                  side_effect=Exception("Scrape error")):
            
            result = await service.web_scrape("tech_id", mock_chat_entity, url="https://example.com")
            
            assert "Error during web scraping" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_get_cyoda_guidelines_success(self, service, mock_chat_entity):
        """Test successful Cyoda guidelines retrieval."""
        with patch('common.utils.web_search.get_cyoda_guidelines', new_callable=AsyncMock, 
                  return_value="Cyoda guidelines content") as mock_guidelines:
            
            result = await service.get_cyoda_guidelines("tech_id", mock_chat_entity)
            
            assert result == "Cyoda guidelines content"
            mock_guidelines.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cyoda_guidelines_error(self, service, mock_chat_entity):
        """Test Cyoda guidelines retrieval with error."""
        with patch('common.utils.web_search.get_cyoda_guidelines', new_callable=AsyncMock, 
                  side_effect=Exception("Guidelines error")):
            
            result = await service.get_cyoda_guidelines("tech_id", mock_chat_entity)
            
            assert "Error getting Cyoda guidelines" in result
            assert mock_chat_entity.failed is True

    @pytest.mark.asyncio
    async def test_web_search_with_custom_params(self, service, mock_chat_entity):
        """Test web search with custom parameters."""
        with patch('common.utils.web_search.web_search', new_callable=AsyncMock, 
                  return_value="Custom search results") as mock_search:
            
            result = await service.web_search(
                "tech_id", mock_chat_entity, 
                query="test query", 
                max_results=10,
                custom_param="value"
            )
            
            assert result == "Custom search results"
            mock_search.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_read_link_with_custom_params(self, service, mock_chat_entity):
        """Test link reading with custom parameters."""
        with patch('common.utils.web_search.read_link', new_callable=AsyncMock, 
                  return_value="Custom link content") as mock_read:
            
            result = await service.read_link(
                "tech_id", mock_chat_entity, 
                url="https://example.com",
                timeout=30,
                headers={"User-Agent": "test"}
            )
            
            assert result == "Custom link content"
            mock_read.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_web_scrape_with_custom_params(self, service, mock_chat_entity):
        """Test web scraping with custom parameters."""
        with patch('common.utils.web_search.web_scrape', new_callable=AsyncMock, 
                  return_value="Custom scraped content") as mock_scrape:
            
            result = await service.web_scrape(
                "tech_id", mock_chat_entity, 
                url="https://example.com",
                selector=".content",
                wait_time=5
            )
            
            assert result == "Custom scraped content"
            mock_scrape.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_get_cyoda_guidelines_with_custom_params(self, service, mock_chat_entity):
        """Test Cyoda guidelines retrieval with custom parameters."""
        with patch('common.utils.web_search.get_cyoda_guidelines', new_callable=AsyncMock, 
                  return_value="Custom guidelines content") as mock_guidelines:
            
            result = await service.get_cyoda_guidelines(
                "tech_id", mock_chat_entity,
                section="api",
                version="v2"
            )
            
            assert result == "Custom guidelines content"
            mock_guidelines.assert_called_once()

    def test_service_inheritance(self, service):
        """Test that service properly inherits from BaseWorkflowService."""
        from tools.base_service import BaseWorkflowService
        assert isinstance(service, BaseWorkflowService)
        assert hasattr(service, 'logger')
        assert hasattr(service, '_handle_error')
        assert hasattr(service, '_validate_required_params')
