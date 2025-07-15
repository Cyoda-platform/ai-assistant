import json
import logging
import aiofiles
from typing import Dict, Any, Optional

import common.config.const as const
from common.config.config import config as env_config
from common.utils.utils import get_project_file_name, get_repository_name

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Handles file operations for workflow dispatcher including reading/writing files,
    managing output configurations, and handling file-based workflows.
    """
    
    def __init__(self, entity_service, cyoda_auth_service):
        """
        Initialize the file handler.
        
        Args:
            entity_service: Service for entity operations
            cyoda_auth_service: Authentication service
        """
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
    
    async def read_config_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read and parse a JSON configuration file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Parsed configuration dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file {file_path}: {e}")
            raise
    
    async def write_output_file(self, file_path: str, content: str) -> None:
        """
        Write content to an output file.
        
        Args:
            file_path: Path to write the file
            content: Content to write
        """
        try:
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(content)
            logger.info(f"Successfully wrote output to {file_path}")
        except Exception as e:
            logger.error(f"Error writing to file {file_path}: {e}")
            raise
    
    async def handle_output_config(self, output_config: Dict[str, Any], content: str, 
                                  entity, technical_id: str) -> None:
        """
        Handle output configuration by writing content to specified destinations.
        
        Args:
            output_config: Output configuration dictionary
            content: Content to output
            entity: Entity for context
            technical_id: Technical identifier
        """
        try:
            # Handle local filesystem output
            local_fs_paths = output_config.get("local_fs", [])
            for file_path in local_fs_paths:
                await self.write_output_file(file_path=file_path, content=content)
            
            # Handle project file output
            project_files = output_config.get("project_file", [])
            for file_path in project_files:
                await self._write_project_file(file_path=file_path, content=content, entity=entity, technical_id=technical_id)
            
            # Handle edge message output
            edge_message_configs = output_config.get("edge_message", [])
            for config in edge_message_configs:
                await self._store_edge_message(config=config, content=content)
                
        except Exception as e:
            logger.error(f"Error handling output config: {e}")
            raise
    
    async def _write_project_file(self, file_path: str, content: str, entity, technical_id: str) -> None:
        """
        Write content to a project file.
        
        Args:
            file_path: Relative file path within the project
            content: Content to write
            entity: Entity for repository context
            technical_id: Technical identifier
        """
        try:
            repository_name = get_repository_name(entity)
            full_path = await get_project_file_name(
                file_name=file_path,
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=repository_name
            )
            await self.write_output_file(full_path, content)
        except Exception as e:
            logger.error(f"Error writing project file {file_path}: {e}")
            raise
    
    async def _store_edge_message(self, config: Dict[str, Any], content: str) -> str:
        """
        Store content as an edge message.
        
        Args:
            config: Edge message configuration
            content: Content to store
            
        Returns:
            Edge message ID
        """
        try:
            edge_message_id = await self.entity_service.add_item(
                token=self.cyoda_auth_service,
                entity_model=config.get("model", const.ModelName.EDGE_MESSAGE_STORE.value),
                entity_version=config.get("version", env_config.ENTITY_VERSION),
                entity=content,
                meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )
            logger.info(f"Stored edge message with ID: {edge_message_id}")
            return edge_message_id
        except Exception as e:
            logger.error(f"Error storing edge message: {e}")
            raise
    
    async def read_input_files(self, input_config: Dict[str, Any], entity, technical_id: str) -> Dict[str, str]:
        """
        Read input files based on configuration.
        
        Args:
            input_config: Input configuration dictionary
            entity: Entity for context
            technical_id: Technical identifier
            
        Returns:
            Dictionary mapping file paths to their contents
        """
        file_contents = {}
        
        try:
            # Handle local filesystem input
            local_fs_paths = input_config.get("local_fs", [])
            for file_path in local_fs_paths:
                async with aiofiles.open(file_path, 'r') as f:
                    file_contents[file_path] = await f.read()
            
            # Handle project file input
            project_files = input_config.get("project_file", [])
            for file_path in project_files:
                content = await self._read_project_file(file_path=file_path, entity=entity, technical_id=technical_id)
                file_contents[file_path] = content
            
            # Handle edge message input
            edge_message_ids = input_config.get("edge_message", [])
            for edge_id in edge_message_ids:
                content = await self._read_edge_message(edge_message_id=edge_id)
                file_contents[f"edge_message_{edge_id}"] = content
                
        except Exception as e:
            logger.error(f"Error reading input files: {e}")
            raise
        
        return file_contents
    
    async def _read_project_file(self, file_path: str, entity, technical_id: str) -> str:
        """
        Read content from a project file.
        
        Args:
            file_path: Relative file path within the project
            entity: Entity for repository context
            technical_id: Technical identifier
            
        Returns:
            File content
        """
        try:
            repository_name = get_repository_name(entity=entity)
            full_path = await get_project_file_name(
                file_name=file_path,
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=repository_name
            )
            async with aiofiles.open(full_path, 'r') as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Error reading project file {file_path}: {e}")
            raise
    
    async def _read_edge_message(self, edge_message_id: str) -> str:
        """
        Read content from an edge message.
        
        Args:
            edge_message_id: Edge message ID
            
        Returns:
            Edge message content
        """
        try:
            content = await self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                entity_version=env_config.ENTITY_VERSION,
                technical_id=edge_message_id,
                meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )
            return content
        except Exception as e:
            logger.error(f"Error reading edge message {edge_message_id}: {e}")
            raise
