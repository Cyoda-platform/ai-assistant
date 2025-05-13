from abc import abstractmethod
from enum import Enum
from typing import List, Any, Optional, Dict

from common.repository.repository import Repository


class DBKeys(Enum):
    CYODA = "CYODA"

class CrudRepository(Repository):
    """
    Abstract base class defining a repository interface for CRUD operations.
    """
    @abstractmethod
    async def get_meta(self, *args, **kwargs):
        return {}

    @abstractmethod
    async def count(self, meta) -> int:
        """
        Returns the number of entities available.
        """
        pass

    @abstractmethod
    async def delete_by_id(self, meta, id: Any) -> None:
        """
        Deletes a given entity.
        """
        pass

    @abstractmethod
    async def delete(self, meta, entity: Any) -> None:
        """
        Deletes a given entity.
        """
        pass

    @abstractmethod
    async def delete_all(self, meta) -> None:
        """
        Deletes all entities managed by the repository.
        """
        pass

    @abstractmethod
    async def delete_all_entities(self, meta, entities: List[Any]) -> None:
        """
        Deletes the given entities.
        """
        pass

    @abstractmethod
    async def delete_all_by_key(self, meta, keys: List[Any]) -> None:
        """
        Deletes all instances of the type T with the given keys.
        """
        pass

    @abstractmethod
    async def delete_by_key(self, meta, key: Any) -> None:
        """
        Deletes the entity with the given key.
        """
        pass

    @abstractmethod
    async def exists_by_key(self, meta, key: Any) -> bool:
        """
        Returns whether an entity with the given key exists.
        """
        pass

    @abstractmethod
    async def find_all(self, meta) -> List[Any]:
        """
        Returns all instances of the type.
        """
        pass

    @abstractmethod
    async def find_all_by_key(self, meta, keys: List[Any]) -> List:
        """
        Returns all instances of the type T with the given keys.
        """
        pass

    @abstractmethod
    async def find_by_key(self, meta, key: Any) -> Optional[Any]:
        """
        Retrieves an entity by its key.
        """
        pass

    @abstractmethod
    async def find_by_id(self, meta, uuid: Any) -> Optional[Any]:
        """
        Retrieves an entity by its technical id.
        """
        pass

    @abstractmethod
    async def find_all_by_criteria(self, meta, criteria: Any) -> Optional[Any]:
        """
        Retrieves an entity by its technical id.
        """
        pass

    @abstractmethod
    async def search_snapshot(
            self,
            meta: Dict[str, str],
            criteria: Any
    ) -> Optional[str]:
        """
        Kick off a new snapshot search for the given entity model/version
        with the provided criteria.

        Returns:
         - snapshot_id (str) once it’s ready
         - None if the server returns 404 (no data)
        """
        pass

    @abstractmethod
    async def get_search_results_page(
            self,
            snapshot_id: str,
            page_number: int = 0,
            page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Given a ready snapshot_id, fetch exactly one page of results.

        Args:
          - snapshot_id: the ID returned by create_search_snapshot
          - page_number: 0-based page index to retrieve
          - page_size: number of items per page

        Returns:
          - list of entity dicts (empty on non-200 or no data)
        """
        pass

    @abstractmethod
    async def save(self, meta, entity: Any) -> Any:
        """
        Saves a given entity.
        """
        pass

    @abstractmethod
    async def save_all(self, meta, entities: List[Any]) -> List[Any]:
        """
        Saves all given entities.
        """
        pass

    @abstractmethod
    async def update(self, meta, technical_id, entity: Any) -> Any:
        """
        Saves all given entities.
        """
        pass

    @abstractmethod
    async def update_all(self, meta, entities: List[Any]) -> List[Any]:
        """
        Saves all given entities.
        """
        pass

    @abstractmethod
    async def get_transitions(self, meta, technical_id):
        """
        Gets next transitions
        """
        pass