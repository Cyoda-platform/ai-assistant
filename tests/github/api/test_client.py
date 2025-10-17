"""
Tests for GitHub API client.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.github.api.client import GitHubAPIClient


class TestGitHubAPIClient:
    """Test GitHubAPIClient."""
    
    def test_client_initialization_default(self):
        with patch('services.github.api.client.config') as mock_config:
            mock_config.GITHUB_API_TOKEN = "test-token"
            mock_config.GH_DEFAULT_OWNER = "test-owner"

            client = GitHubAPIClient()
            assert client.token == "test-token"
            assert client.owner == "test-owner"
            assert client.BASE_URL == "https://api.github.com"
    
    def test_client_initialization_custom(self):
        client = GitHubAPIClient(token="custom-token", owner="custom-owner")
        assert client.token == "custom-token"
        assert client.owner == "custom-owner"
    
    def test_headers_property(self):
        client = GitHubAPIClient(token="test-token")
        headers = client._get_headers()

        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Accept"] == "application/vnd.github+json"
        assert headers["X-GitHub-Api-Version"] == "2022-11-28"
        assert headers["Content-Type"] == "application/json"
    
    @pytest.mark.asyncio
    async def test_request_success(self):
        client = GitHubAPIClient(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_httpx:
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.get = AsyncMock(return_value=mock_response)
            mock_httpx_instance.post = AsyncMock(return_value=mock_response)
            mock_httpx_instance.put = AsyncMock(return_value=mock_response)
            mock_httpx_instance.delete = AsyncMock(return_value=mock_response)
            mock_httpx_instance.patch = AsyncMock(return_value=mock_response)
            mock_httpx.return_value.__aenter__.return_value = mock_httpx_instance

            result = await client.request("GET", "test/endpoint")
            assert result == {"data": "test"}
    
    @pytest.mark.asyncio
    async def test_request_with_params(self):
        client = GitHubAPIClient(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_httpx:
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.get = AsyncMock(return_value=mock_response)
            mock_httpx.return_value.__aenter__.return_value = mock_httpx_instance

            result = await client.request("GET", "test/endpoint", params={"key": "value"})
            assert result == {"data": "test"}
    
    @pytest.mark.asyncio
    async def test_request_with_data(self):
        client = GitHubAPIClient(token="test-token")

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"created": True}
        mock_response.raise_for_status = MagicMock()

        with patch('httpx.AsyncClient') as mock_httpx:
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.post = AsyncMock(return_value=mock_response)
            mock_httpx.return_value.__aenter__.return_value = mock_httpx_instance

            result = await client.request("POST", "test/endpoint", data={"key": "value"})
            assert result == {"created": True}
    
    @pytest.mark.asyncio
    async def test_request_error(self):
        client = GitHubAPIClient(token="test-token")
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = Exception("404 error")
        
        with patch('httpx.AsyncClient') as mock_httpx:
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.request = AsyncMock(return_value=mock_response)
            mock_httpx.return_value.__aenter__.return_value = mock_httpx_instance
            
            with pytest.raises(Exception):
                await client.request("GET", "test/endpoint")
    
    @pytest.mark.asyncio
    async def test_get_method(self):
        client = GitHubAPIClient(token="test-token")
        
        with patch.object(client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"data": "test"}
            
            result = await client.get("test/endpoint", params={"key": "value"})
            mock_request.assert_called_once_with("GET", "test/endpoint", params={"key": "value"})
            assert result == {"data": "test"}
    
    @pytest.mark.asyncio
    async def test_post_method(self):
        client = GitHubAPIClient(token="test-token")
        
        with patch.object(client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"created": True}
            
            result = await client.post("test/endpoint", data={"key": "value"})
            mock_request.assert_called_once_with("POST", "test/endpoint", data={"key": "value"})
            assert result == {"created": True}
    
    @pytest.mark.asyncio
    async def test_put_method(self):
        client = GitHubAPIClient(token="test-token")
        
        with patch.object(client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"updated": True}
            
            result = await client.put("test/endpoint", data={"key": "value"})
            mock_request.assert_called_once_with("PUT", "test/endpoint", data={"key": "value"})
            assert result == {"updated": True}
    
    @pytest.mark.asyncio
    async def test_delete_method(self):
        client = GitHubAPIClient(token="test-token")
        
        with patch.object(client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"deleted": True}
            
            result = await client.delete("test/endpoint")
            mock_request.assert_called_once_with("DELETE", "test/endpoint")
            assert result == {"deleted": True}
    
    @pytest.mark.asyncio
    async def test_patch_method(self):
        client = GitHubAPIClient(token="test-token")
        
        with patch.object(client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"patched": True}
            
            result = await client.patch("test/endpoint", data={"key": "value"})
            mock_request.assert_called_once_with("PATCH", "test/endpoint", data={"key": "value"})
            assert result == {"patched": True}
    
    @pytest.mark.asyncio
    async def test_download_file(self):
        client = GitHubAPIClient(token="test-token")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"file content"
        
        with patch('httpx.AsyncClient') as mock_httpx:
            mock_httpx_instance = AsyncMock()
            mock_httpx_instance.get = AsyncMock(return_value=mock_response)
            mock_httpx.return_value.__aenter__.return_value = mock_httpx_instance
            
            result = await client.download_file("https://example.com/file.zip")
            assert result == b"file content"

