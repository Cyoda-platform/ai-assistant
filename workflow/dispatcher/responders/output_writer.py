"""OutputWriter for handling output writing to various destinations."""

import asyncio
import json
import logging
from typing import Dict, Any
from entity.chat.chat import AgenticFlowEntity
from common.config.config import config as env_config
import common.config.const as const
from common.utils.utils import _save_file, get_repository_name
from workflow.dispatcher.events.processing_context import ProcessingContext
from workflow.dispatcher.events.services import Services

logger = logging.getLogger(__name__)


class OutputWriter:
    """Handles writing output to various destinations."""
    
    def __init__(self, write_output_lock: asyncio.Lock):
        self._write_output_lock = write_output_lock
    
    async def write(self, ctx: ProcessingContext, response: str) -> None:
        """Write response to configured outputs."""
        if not isinstance(ctx.event.entity, AgenticFlowEntity):
            return
        
        config = ctx.config
        if not config or not config.get("output"):
            return
        
        # Handle output writing with lock protection
        async with self._write_output_lock:
            await self._write_to_output(
                entity=ctx.event.entity,
                config=config,
                response=response,
                technical_id=ctx.event.technical_id,
                services=ctx.services
            )
    
    async def _write_to_output(self, entity: AgenticFlowEntity, config: Dict[str, Any],
                              response: str, technical_id: str, services: Services) -> None:
        """Write response to output if configured."""
        if config.get("output"):
            if config.get("output").get("local_fs"):
                local_files = config.get("output").get("local_fs")
                for cache_key in local_files:
                    if cache_key.endswith(".json"):
                        try:
                            parsed_json = json.loads(response)
                            response = json.dumps(parsed_json, indent=4, sort_keys=True)
                        except json.JSONDecodeError as err:
                            logger.error(f"Invalid JSON format for file {cache_key}: {err}")
                    try:
                        formatted_filename = cache_key.format(**entity.workflow_cache)
                    except Exception as e:
                        formatted_filename = cache_key
                        logger.exception(e)
                    branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
                    await _save_file(_data=response,
                                   item=formatted_filename,
                                   git_branch_id=branch_id,
                                   repository_name=get_repository_name(entity))
            if config.get("output").get("workflow_cache"):
                cache_keys = config.get("output").get("workflow_cache")
                for cache_key in cache_keys:
                    entity.workflow_cache[cache_key] = response
            if config.get("output").get("cyoda_edge_message"):
                edge_messages = config.get("output").get("cyoda_edge_message")
                for edge_message in edge_messages:
                    edge_message_id = await services.entity_service.add_item(
                        token=services.cyoda_auth_service,
                        entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                        entity_version=env_config.ENTITY_VERSION,
                        entity=response,
                        meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                    )
                    entity.edge_messages_store[edge_message] = edge_message_id
