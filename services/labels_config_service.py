import logging
import httpx
from typing import Any, Dict, Optional
from common.config.config import config

_logger = logging.getLogger(__name__)

class LabelsConfigService:
    def __init__(self) -> None:
        self._base_url = config.CONFIG_URL.rstrip('/')
        self._file_name = config.UI_LABELS_CONFIG_FILE_NAME
        self._cache: Dict[str, Any] = {}

    @property
    def _url(self) -> str:
        return f"{self._base_url}/{self._file_name}"

    async def refresh(self) -> None:
        """
        Fetch from remote and overwrite the cache.
        Opens a fresh HTTP client for this single operation.
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self._url)
                resp.raise_for_status()
                self._cache = resp.json()
        except httpx.HTTPError as e:
            _logger.error("Unable to reload labels config from %s: %s", self._url, e)
            raise

    async def get_all(self) -> Dict[str, Any]:
        """
        Return the cached config, loading it on first call (which will open/close a client).
        """
        if not self._cache:
            await self.refresh()
        return self._cache

    async def get(self, identifier: str) -> Optional[Any]:
        """
        Retrieve a value by dotted path, e.g. 'side_bar.links.home'.
        Returns None if missing.
        """
        data = await self.get_all()
        current: Any = data
        for part in identifier.replace('-', '_').split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current