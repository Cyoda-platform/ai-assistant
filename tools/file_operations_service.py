import asyncio
import json
import os
import aiofiles
from typing import List

import common.config.const as const
from common.config.config import config
from common.utils.utils import (
    get_project_file_name, _git_push, _save_file, clone_repo,
    read_file_util, delete_file, delete_directory
)
from tools.repository_resolver import resolve_repository_name_with_language_param
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService


class FileOperationsService(BaseWorkflowService):
    """
    Service responsible for all file-related operations including
    saving, reading, cloning repositories, and file management.
    """

    def __init__(self,
                 workflow_helper_service,
                 entity_service,
                 cyoda_auth_service,
                 workflow_converter_service,
                 scheduler_service,
                 data_service,
                 dataset=None,
                 mock=False):
        super().__init__(
            workflow_helper_service=workflow_helper_service,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            workflow_converter_service=workflow_converter_service,
            scheduler_service=scheduler_service,
            data_service=data_service,
            dataset=dataset,
            mock=mock
        )
        self._file_write_lock = asyncio.Lock()
        self._file_delete_lock = asyncio.Lock()

    async def save_env_file(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Save environment file with chat ID replacement.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including filename
            
        Returns:
            Success message or error
        """
        try:
            # Use repository resolver to determine repository name
            repository_name = entity.workflow_cache.get(const.REPOSITORY_NAME_PARAM, technical_id)
            file_name = await get_project_file_name(
                file_name=params.get("filename"),
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=repository_name
            )
            
            async with aiofiles.open(file_name, 'r') as template_file:
                content: str = await template_file.read()

            # Replace CHAT_ID_VAR with technical_id
            env_name = f"client-{entity.user_id.lower()}.{config.CLIENT_HOST}"

            updated_content = (content.replace('CHAT_ID_VAR', technical_id)
                               .replace('YOUR_ENV_NAME_VAR', env_name))

            # Save the updated content to the file with lock protection
            async with self._file_write_lock:
                async with aiofiles.open(file_name, 'w') as new_file:
                    await new_file.write(updated_content)

                await _git_push(git_branch_id=technical_id,
                                file_paths=[file_name],
                                commit_message="Added env file template",
                                repository_name=repository_name)
            return "🧩.env.template file saved successfully. Proceeding to the next step⏳...You will see a notification soon!"
            
        except Exception as e:
            self.logger.exception("Error saving environment file: %s", str(e))
            return self._handle_error(entity, e, "Error saving environment file")

    async def save_file(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Save data to a file using the provided chat id and file name.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including filename and new_content
            
        Returns:
            Success message or error
        """
        try:
            is_valid, error_msg = await self._validate_required_params(
                params, ["filename", "new_content"]
            )
            if not is_valid:
                return error_msg

            # Use repository resolver to determine repository name
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")
            if repository_name.startswith("java"):
                new_content = params.get("new_content")
            else:
                new_content = self.parse_from_string(escaped_code=params.get("new_content"))

            async with self._file_write_lock:
                await _save_file(
                    _data=new_content,
                    item=params.get("filename"),
                    git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                    repository_name=repository_name
                )
            return "File saved successfully"
            
        except Exception as e:
            self.logger.exception("Error during saving file: %s", str(e))
            return self._handle_error(entity, e, "Error during saving file")

    async def get_file_contents(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Get file contents by path for agent use.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including file_path

        Returns:
            File content or error message
        """
        try:
            is_valid, error_msg = await self._validate_required_params(params, ["file_path"])
            if not is_valid:
                return error_msg

            # Use repository resolver to determine repository name
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            return await read_file_util(
                filename=params.get("file_path"),
                technical_id=technical_id,
                repository_name=repository_name,
                git_branch_id=git_branch_id
            )

        except Exception as e:
            self.logger.exception("Error reading file: %s", str(e))
            return self._handle_error(entity, e, "Error reading file")

    async def list_directory_files(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        List all files in a directory recursively for agent use.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including directory_path

        Returns:
            JSON string with list of files (including subdirectories) or error message
        """
        try:
            is_valid, error_msg = await self._validate_required_params(params, ["directory_path"])
            if not is_valid:
                return error_msg

            directory_path = params.get("directory_path")
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            # Use repository resolver to determine repository name
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")

            # Get full directory path
            full_directory_path = await get_project_file_name(
                file_name=directory_path,
                git_branch_id=git_branch_id,
                repository_name=repository_name
            )

            # List files recursively in directory using async operations
            if await self._directory_exists(full_directory_path):
                files = await self._get_all_files_recursively(full_directory_path)

                return json.dumps({
                    "directory": directory_path,
                    "files": sorted(files),
                    "count": len(files),
                    "recursive": True
                })
            else:
                return json.dumps({
                    "directory": directory_path,
                    "files": [],
                    "count": 0,
                    "recursive": True,
                    "message": "Directory does not exist or is not accessible"
                })

        except Exception as e:
            self.logger.exception("Error listing directory files: %s", str(e))
            return self._handle_error(entity, e, "Error listing directory files")

    async def _directory_exists(self, directory_path: str) -> bool:
        """
        Check if directory exists asynchronously.

        Args:
            directory_path: Path to directory

        Returns:
            True if directory exists and is a directory
        """
        try:
            return os.path.exists(directory_path) and os.path.isdir(directory_path)
        except Exception as e:
            self.logger.debug("Error checking directory existence for %s: %s", directory_path, str(e))
            return False

    async def _list_files_in_directory(self, directory_path: str) -> List[str]:
        """
        List files in directory asynchronously.

        Args:
            directory_path: Path to directory

        Returns:
            List of file names
        """
        try:
            files = []
            for file_name in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file_name)
                if os.path.isfile(file_path):
                    files.append(file_name)
            return files
        except Exception as e:
            self.logger.debug("Error listing files in directory %s: %s", directory_path, str(e))
            return []

    async def _get_all_files_recursively(self, directory_path: str) -> List[str]:
        """
        Get all files recursively from directory and all subdirectories.

        Args:
            directory_path: Path to directory

        Returns:
            List of relative file paths from the root directory
        """
        try:
            import asyncio

            def _walk_directory_sync():
                files = []
                for root, dirs, file_names in os.walk(directory_path):
                    # Filter out hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.')]

                    for file_name in file_names:
                        # Skip hidden files
                        if file_name.startswith('.'):
                            continue

                        # Get relative path from the root directory
                        full_file_path = os.path.join(root, file_name)
                        relative_path = os.path.relpath(full_file_path, directory_path)
                        files.append(relative_path)

                return files

            return await asyncio.to_thread(_walk_directory_sync)
        except Exception as e:
            self.logger.debug("Error walking directory %s: %s", directory_path, str(e))
            return []

    async def get_entity_pojo_contents(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Get entity POJO contents to understand the data model.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including entity_name

        Returns:
            Entity POJO content or error message
        """
        try:
            is_valid, error_msg = await self._validate_required_params(params, ["entity_name"])
            if not is_valid:
                return error_msg

            entity_name = params.get("entity_name")

            # Use repository resolver to determine repository name
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            # Try common entity POJO paths
            possible_paths = [
                f"src/main/java/com/java_template/application/entity/{entity_name}.java",
                f"src/main/java/com/java_template/application/entity/{entity_name}Entity.java",
            ]

            for entity_path in possible_paths:
                try:
                    content = await read_file_util(
                        filename=entity_path,
                        technical_id=technical_id,
                        repository_name=repository_name,
                        git_branch_id=git_branch_id
                    )
                    if content and content.strip():
                        return f"Entity POJO found at {entity_path}:\n\n{content}"
                except Exception as e:
                    self.logger.debug("Entity POJO not found at path %s: %s", entity_path, str(e))
                    continue

            return f"Entity POJO not found for '{entity_name}'. Tried paths: {', '.join(possible_paths)}"

        except Exception as e:
            self.logger.exception("Error reading entity POJO: %s", str(e))
            return self._handle_error(entity, e, "Error reading entity POJO")

    async def read_file(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Read data from a file using the provided chat id and file name.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including filename
            
        Returns:
            File content or error message
        """
        try:
            is_valid, error_msg = await self._validate_required_params(params, ["filename"])
            if not is_valid:
                return error_msg
                
            # Use repository resolver to determine repository name
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            return await read_file_util(
                filename=params.get("filename"),
                technical_id=technical_id,
                repository_name=repository_name,
                git_branch_id=git_branch_id
            )
            
        except Exception as e:
            self.logger.exception("Error reading file: %s", str(e))
            return self._handle_error(entity, e, "Error reading file")

    async def clone_repo(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Clone the GitHub repository to the target directory.
        If the repository should not be copied, it ensures the target directory exists.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters
            
        Returns:
            Success message with branch information
        """
        try:
            # Use repository resolver to determine repository name
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")

            async with self._file_write_lock:
                await clone_repo(git_branch_id=technical_id, repository_name=repository_name)

                # Call the async _save_file function
                await _save_file(
                    _data=technical_id,
                    item='README.txt',
                    git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                    repository_name=repository_name
                )
            
            # Update workflow cache
            entity.workflow_cache[const.GIT_BRANCH_PARAM] = technical_id
            entity.workflow_cache[const.REPOSITORY_NAME_PARAM] = repository_name
            return const.BRANCH_READY_NOTIFICATION.format(
                repository_name=repository_name, 
                git_branch=technical_id
            )
            
        except Exception as e:
            self.logger.exception("Error cloning repository: %s", str(e))
            return self._handle_error(entity, e, "Error cloning repository")

    async def delete_files(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Delete multiple files and directories from the repository.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including files list and directories list

        Returns:
            Empty string on success or error message
        """
        try:
            files: List[str] = params.get("files", [])
            directories: List[str] = params.get("directories", [])

            if not files and not directories:
                return "No files or directories specified for deletion"

            # Use repository resolver to determine repository name
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")
            git_branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            async with self._file_delete_lock:
                # Delete files
                for file_name in files:
                    await delete_file(
                        _data=technical_id,
                        item=file_name,
                        git_branch_id=git_branch_id,
                        repository_name=repository_name
                    )

                # Delete directories
                for directory_name in directories:
                    await delete_directory(
                        _data=technical_id,
                        item=directory_name,
                        git_branch_id=git_branch_id,
                        repository_name=repository_name
                    )

            return ""

        except Exception as e:
            self.logger.exception("Error deleting files and directories: %s", str(e))
            return self._handle_error(entity, e, "Error deleting files and directories")

    async def save_entity_templates(self, technical_id: str, entity: ChatEntity, **params) -> str:
        """
        Save entity templates from design data.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Additional parameters
            
        Returns:
            Success message or error
        """
        try:
            # Use repository resolver to determine repository name
            repository_name = resolve_repository_name_with_language_param(entity, "JAVA")

            file_path = await get_project_file_name(
                file_name="entity/entities_data_design.json",
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=repository_name
            )

            async with aiofiles.open(file_path, 'r') as f:
                file_contents = await f.read()
            entity_design_data = json.loads(file_contents)

            entities = entity_design_data.get("entities", [])

            async with self._file_write_lock:
                for entity_data in entities:
                    entity_name = entity_data.get('entity_name')
                    entity_data_example = entity_data.get('entity_data_example')

                    if not entity_name:
                        self.logger.warning("Missing 'entity_name' in entity data: %s", entity_data)
                        continue

                    target_item = f"entity/{entity_name}/{entity_name}.json"
                    data_str = json.dumps(
                        entity_data_example, indent=4, sort_keys=True
                    ) if entity_data_example is not None else "{}"

                    await _save_file(
                        _data=data_str,
                        item=target_item,
                        git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                        repository_name=repository_name
                    )
                
            return "Entity templates saved successfully"

        except Exception as e:
            self.logger.exception("Error saving entity templates: %s", str(e))
            return self._handle_error(entity, e, "Error saving entity templates")

    async def add_application_resource(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:

        validation_result = await self._validate_required_params(
            params, ["resource_path", "file_contents"]
        )
        is_valid, error_message = validation_result
        if not is_valid:
            return error_message

        # Extract validated parameters
        resource_path = params["resource_path"]
        file_contents = params["file_contents"]

        # Validate resource path security
        if self._is_unsafe_path(resource_path):
            return "Error: Invalid resource path. Path must be relative and not contain '..' or start with '/'"

        try:
            # Determine repository and branch information
            repository_name = self._get_repository_name(entity)
            git_branch_id = self._get_git_branch_id(entity, technical_id)

            # Log the operation
            self._log_resource_operation(resource_path, entity, repository_name)

            # Save the resource file with lock protection
            async with self._file_write_lock:
                await _save_file(
                    _data=file_contents,
                    item=resource_path,
                    git_branch_id=git_branch_id,
                    repository_name=repository_name
                )

            # Return success message
            character_count = len(file_contents)
            return f"Successfully added application resource: {resource_path} ({character_count} characters)"

        except Exception as error:
            self.logger.exception("Error adding application resource: %s", str(error))
            return self._handle_error(entity, error, f"Error adding application resource: {error}")

    def _is_unsafe_path(self, path: str) -> bool:
        """Check if a resource path is unsafe for security reasons.

        Args:
            path: Resource path to validate

        Returns:
            True if path is unsafe, False if safe
        """
        if not path:
            return True
        if path.startswith('/'):
            return True
        if '..' in path:
            return True
        return False

    def _get_repository_name(self, entity: AgenticFlowEntity) -> str:
        """Get repository name for the entity using the resolver.

        Args:
            entity: Agentic flow entity

        Returns:
            Repository name
        """
        return resolve_repository_name_with_language_param(entity, "JAVA")

    def _get_git_branch_id(self, entity: AgenticFlowEntity, technical_id: str) -> str:
        """Get git branch ID from entity cache or fallback to technical ID.

        Args:
            entity: Agentic flow entity
            technical_id: Technical identifier as fallback

        Returns:
            Git branch identifier
        """
        if const.GIT_BRANCH_PARAM in entity.workflow_cache:
            return entity.workflow_cache[const.GIT_BRANCH_PARAM]
        return technical_id

    def _log_resource_operation(self, resource_path: str, entity: AgenticFlowEntity, repository_name: str) -> None:
        """Log the resource addition operation for debugging.

        Args:
            resource_path: Path of the resource being added
            entity: Agentic flow entity
            repository_name: Name of the target repository
        """
        programming_language = "unknown"
        if "programming_language" in entity.workflow_cache:
            programming_language = entity.workflow_cache["programming_language"]

        self.logger.info(
            f"Adding application resource: {resource_path} "
            f"for {programming_language} project in {repository_name}"
        )
