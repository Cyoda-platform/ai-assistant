import threading
import json
import logging
import time
import asyncio
from typing import List, Any, Optional, Tuple, Dict
import common.config.const as const
from common.config.config import config
from common.repository.crud_repository import CrudRepository
from common.utils.utils import (
    custom_serializer,
    send_cyoda_request,
)

logger = logging.getLogger(__name__)

# In-memory cache for edge-message entities
_edge_messages_cache = {}


class CyodaRepository(CrudRepository):
    """
    Thread-safe singleton repository for interacting with the Cyoda API.
    Retries once on HTTP 401 by invalidating tokens and fetching fresh ones.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, cyoda_auth_service):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._cyoda_auth_service = cyoda_auth_service
        return cls._instance


    async def _wait_for_search_completion(
        self,
        snapshot_id: str,
        timeout: float = 60.0,
        interval: float = 0.3
    ) -> None:
        """
        Poll the snapshot status endpoint until SUCCESSFUL or error/timeout.
        """
        start = time.monotonic()
        status_path = f"search/snapshot/{snapshot_id}/status"

        while True:
            resp = await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method="get", path=status_path)
            if resp.get("status") != 200:
                return
            status = resp.get("json", {}).get("snapshotStatus")
            if status == "SUCCESSFUL":
                return
            if status not in ("RUNNING",):
                raise Exception(f"Snapshot search failed: {resp.get('json')}")
            if time.monotonic() - start > timeout:
                raise TimeoutError(f"Timeout exceeded after {timeout} seconds")
            await asyncio.sleep(interval)

    async def delete(self, meta, entity: Any) -> None:
        pass

    async def get_meta(self, token, entity_model, entity_version):
        return {"token": token, "entity_model": entity_model, "entity_version": entity_version}

    async def count(self, meta) -> int:
        items = await self.find_all(meta)
        return len(items)

    async def delete_all(self, meta) -> None:
        path = f"entity/{meta['entity_model']}/{meta['entity_version']}"
        await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method="delete", path=path)

    async def delete_all_entities(self, meta, entities: List[Any]) -> None:
        for entity in entities:
            technical_id = getattr(entity, 'technical_id', entity)
            await self.delete_by_id(meta, technical_id)

    async def delete_all_by_key(self, meta, keys: List[Any]) -> None:
        for key in keys:
            await self.delete_by_key(meta, key)

    async def delete_by_key(self, meta, key: Any) -> None:
        entity = await self.find_by_key(meta, key)
        if entity and 'technical_id' in entity:
            await self.delete_by_id(meta, entity['technical_id'])

    async def exists_by_key(self, meta, key: Any) -> bool:
        return (await self.find_by_key(meta, key)) is not None

    #does not return current_state!
    async def find_all(self, meta) -> List[Any]:
        path = f"entity/{meta['entity_model']}/{meta['entity_version']}?pageSize={const.CYODA_PAGE_SIZE}"
        resp = await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method="get", path=path)
        return resp.get("json", [])

    async def find_all_by_key(self, meta, keys: List[Any]) -> List[Any]:
        results = []
        for key in keys:
            entity = await self.find_by_key(meta, key)
            if entity:
                results.append(entity)
        return results

    async def find_by_key(self, meta, key: Any) -> Optional[Any]:
        # If the user has pre‑set meta["condition"], use that; otherwise search by {"key": key}
        criteria = meta.get("condition") or {"key": key}
        entities = await self.find_all_by_criteria(meta, criteria)
        return entities[0] if entities else None

    async def find_by_id(self, meta, _uuid: Any) -> Optional[Any]:
        method = "get"
        if meta and meta.get("type") == config.CYODA_ENTITY_TYPE_EDGE_MESSAGE:
            if _uuid in _edge_messages_cache:
                return _edge_messages_cache[_uuid]
            path = f"message/get/{_uuid}"
            resp = await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method=method, path=path)
            content = resp.get("json", {}).get("content", "{}")
            data = json.loads(content).get("edge_message_content")
            if data:
                _edge_messages_cache[_uuid] = data
            return data

        path = f"entity/{_uuid}"

        resp = await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method=method, path=path)
        if not isinstance(resp, dict):
            logger.exception(f"method = {method}, path = {path}")
            logger.error(f"resp = {resp} ")
            raise Exception("find_by_id resp is not dict!")
        payload = resp.get("json", {})
        if not isinstance(payload, dict):
            logger.exception(f"method = {method}, path = {path}")
            logger.error(f"payload = {payload} ")
            logger.error(f"resp = {resp} ")
            raise Exception("find_by_id payload is not dict!")
        data = payload.get("data", {})
        data["current_state"] = payload.get("meta", {}).get("state")
        data["technical_id"] = _uuid
        return data

    async def find_all_by_criteria(self, meta, criteria: Any) -> List[Any]:
        # 1) trigger snapshot
        snap_path = f"search/snapshot/{meta['entity_model']}/{meta['entity_version']}"
        resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="post",
            path=snap_path,
            data=json.dumps(criteria)
        )
        snapshot_id = resp.get("json")
        if resp.get('status') == 404:
            return []

        # 2) poll until ready
        await self._wait_for_search_completion(snapshot_id)

        # 3) fetch all results, page by page
        entities: List[Any] = []
        page_number = 0
        page_size = 100  # match your initial request

        # first request so we can read totalElements/totalPages
        result_resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="get",
            path=f"search/snapshot/{snapshot_id}?pageSize={page_size}&pageNumber={page_number}"
        )
        if result_resp.get("status") != 200:
            return []

        resp_json = json.loads(result_resp.get("json", "{}"))
        page_info = resp_json.get("page", {})

        # **zero‐results guard**
        if page_info.get("totalElements", 0) == 0:
            return []

        total_pages = page_info.get("totalPages", 1)

        # helper to extract & normalize nodes
        def _extract(nodes):
            for node in nodes:
                tree = node.get("data", {})
                if not tree.get("technical_id"):
                    tree["technical_id"] = node.get("meta", {}).get("id")
                    tree["current_state"] = node.get("meta", {}).get("state")
                entities.append(tree)

        # process page 0
        _extract(resp_json.get("_embedded", {}).get("objectNodes", []))

        # fetch remaining pages (1 through total_pages-1)
        for page_number in range(1, total_pages):
            result_resp = await send_cyoda_request(
                cyoda_auth_service=self._cyoda_auth_service,
                method="get",
                path=f"search/snapshot/{snapshot_id}?pageSize={page_size}&pageNumber={page_number}"
            )
            if result_resp.get("status") != 200:
                break  # or continue, per your error‐handling policy

            resp_json = json.loads(result_resp.get("json", "{}"))
            _extract(resp_json.get("_embedded", {}).get("objectNodes", []))

        return entities

    async def search_snapshot(
        self,
        meta: Dict[str, str],
        criteria: Any
    ) -> Optional[str]:
        snap_path = f"search/snapshot/{meta['entity_model']}/{meta['entity_version']}"
        resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="post",
            path=snap_path,
            data=json.dumps(criteria),
        )

        if resp.get("status") == 404:
            return None

        snapshot_id = resp.get("json")
        await self._wait_for_search_completion(snapshot_id)
        return snapshot_id


    async def get_search_results_page(
        self,
        snapshot_id: str,
        page_number: int = 0,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Given a ready snapshot_id, fetch exactly one page of results.
        Returns an empty list on any non-200 response or if the page is empty.
        """
        path = (
            f"search/snapshot/{snapshot_id}"
            f"?pageSize={page_size}&pageNumber={page_number}"
        )
        resp = await send_cyoda_request(
            cyoda_auth_service=self._cyoda_auth_service,
            method="get",
            path=path,
        )

        if resp.get("status") != 200:
            return []

        body = json.loads(resp.get("json", "{}"))
        nodes = body.get("_embedded", {}).get("objectNodes", [])
        results: List[Dict[str, Any]] = []

        for node in nodes:
            data = node.get("data", {})
            if not data.get("technical_id"):
                data["technical_id"] = node.get("meta", {}).get("id")
                data["current_state"] = node.get("meta", {}).get("state")
            results.append(data)

        return results


    async def save(self, meta, entity: Any) -> Any:
        if meta.get("type") == config.CYODA_ENTITY_TYPE_EDGE_MESSAGE:
            payload = {
                "meta-data": {"source": "ai_assistant"},
                "payload": {"edge_message_content": entity},
            }
            data = json.dumps(payload, default=custom_serializer)
            path = f"message/new/{meta['entity_model']}_{meta['entity_version']}"
        else:
            data = json.dumps(entity, default=custom_serializer)
            path = f"entity/JSON/{meta['entity_model']}/{meta['entity_version']}"

        resp = await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method="post", path=path, data=data)
        result = resp.get("json", [])

        technical_id = None
        if isinstance(result, list) and result:
            technical_id = result[0].get("entityIds", [None])[0]

        if meta.get("type") == config.CYODA_ENTITY_TYPE_EDGE_MESSAGE and technical_id:
            _edge_messages_cache[technical_id] = entity

        return technical_id

    async def save_all(self, meta, entities: List[Any]) -> Any:
        # restore v1 behavior: return first entity ID only
        data = json.dumps(entities, default=custom_serializer)
        path = f"entity/JSON/{meta['entity_model']}/{meta['entity_version']}"
        resp = await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method="post", path=path, data=data)
        result = resp.get("json", [])

        technical_id = None
        if isinstance(result, list) and result:
            technical_id = result[0].get("entityIds", [None])[0]

        return technical_id

    async def update(self, meta, technical_id: Any, entity: Any = None) -> Any:
        if entity is None:
            return await self._launch_transition(meta=meta, technical_id=technical_id)

        transition = meta.get("update_transition", const.TransitionKey.UPDATE.value)
        path = (
            f"entity/JSON/{technical_id}/{transition}"
            "?transactional=true&waitForConsistencyAfter=true"
        )
        data = json.dumps(entity, default=custom_serializer)
        resp = await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method="put", path=path, data=data)
        result = resp.get("json", {})
        if not isinstance(result, dict):
            logger.exception(result)
            return None
        return result.get("entityIds", [None])[0]

    async def update_all(self, meta, entities: List[Any]) -> List[Any]:
        payload = []
        for ent in entities:
            payload.append({
                "id": meta.get("technical_id"),
                "transition": meta.get("update_transition", const.TransitionKey.UPDATE.value),
                "payload": json.dumps(ent, default=custom_serializer),
            })
        data = json.dumps(payload)
        path = "entity/JSON"
        await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method="put", path=path, data=data)
        return entities

    async def delete_by_id(self, meta, technical_id: Any) -> None:
        path = f"entity/{technical_id}"
        await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method="delete", path=path)

    async def get_transitions(self, meta, technical_id: Any) -> Any:
        entity_class = (
            const.JavaClasses.EDGE_MESSAGE.value
            if meta.get("type") == config.CYODA_ENTITY_TYPE_EDGE_MESSAGE
            else const.JavaClasses.TREE_NODE_ENTITY.value
        )
        path = (
            f"platform-api/entity/fetch/transitions?entityClass={entity_class}"
            f"&entityId={technical_id}"
        )
        resp = await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method="get", path=path)
        return resp.get("json")

    async def _launch_transition(self, meta, technical_id):
        entity_class = (
            const.JavaClasses.EDGE_MESSAGE.value
            if meta.get("type") == config.CYODA_ENTITY_TYPE_EDGE_MESSAGE
            else const.JavaClasses.TREE_NODE_ENTITY.value
        )
        path = (
            f"platform-api/entity/transition?entityId={technical_id}"
            f"&entityClass={entity_class}&transitionName="
            f"{meta.get('update_transition', const.TransitionKey.UPDATE.value)}"
        )
        resp = await send_cyoda_request(cyoda_auth_service=self._cyoda_auth_service, method="put", path=path)
        return resp.get("json")
