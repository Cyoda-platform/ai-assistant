import json
import aiofiles
from typing import List

import common.config.const as const
from common.config.config import config
from common.utils.utils import (
    get_project_file_name, _git_push, _save_file, clone_repo,
    parse_from_string, read_file_util, get_repository_name, delete_file
)
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService


class FileOperationsService(BaseWorkflowService):
    """
    Service responsible for all file-related operations including
    saving, reading, cloning repositories, and file management.
    """

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
            repository_name = get_repository_name(entity)
            file_name = await get_project_file_name(
                file_name=params.get("filename"),
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=repository_name
            )
            
            async with aiofiles.open(file_name, 'r') as template_file:
                content = await template_file.read()

            # Replace CHAT_ID_VAR with technical_id
            updated_content = content.replace('CHAT_ID_VAR', technical_id)

            # Save the updated content to the file
            async with aiofiles.open(file_name, 'w') as new_file:
                await new_file.write(updated_content)
                
            await _git_push(technical_id, [file_name], "Added env file template", repository_name=repository_name)
            return "Environment file saved successfully"
            
        except Exception as e:
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
                
            repository_name = get_repository_name(entity)
            if repository_name.startswith("java"):
                new_content = params.get("new_content")
            else:
                new_content = self.parse_from_string(escaped_code=params.get("new_content"))
                
            await _save_file(
                _data=new_content,
                item=params.get("filename"),
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=repository_name
            )
            return "File saved successfully"
            
        except Exception as e:
            return self._handle_error(entity, e, "Error during saving file")

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
                
            return await read_file_util(
                filename=params.get("filename"),
                technical_id=technical_id,
                repository_name=get_repository_name(entity)
            )
            
        except Exception as e:
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
            repository_name = get_repository_name(entity)

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
            return const.BRANCH_READY_NOTIFICATION.format(
                repository_name=repository_name, 
                git_branch=technical_id
            )
            
        except Exception as e:
            return self._handle_error(entity, e, "Error cloning repository")

    async def delete_files(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Delete multiple files from the repository.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including files list
            
        Returns:
            Empty string on success or error message
        """
        try:
            files: List[str] = params.get("files", [])
            if not files:
                return "No files specified for deletion"
                
            for file_name in files:
                await delete_file(
                    _data=technical_id,
                    item=file_name,
                    git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                    repository_name=get_repository_name(entity)
                )
            return ""
            
        except Exception as e:
            return self._handle_error(entity, e, "Error deleting files")

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
            file_path = await get_project_file_name(
                file_name="entity/entities_data_design.json",
                git_branch_id=entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id),
                repository_name=get_repository_name(entity)
            )

            async with aiofiles.open(file_path, 'r') as f:
                file_contents = await f.read()
            entity_design_data = json.loads(file_contents)

            entities = entity_design_data.get("entities", [])

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
                    repository_name=get_repository_name(entity)
                )
                
            return "Entity templates saved successfully"

        except Exception as e:
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

            # Save the resource file
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
        from tools.repository_resolver import resolve_repository_name
        return resolve_repository_name(entity)

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
