import json
from typing import Any

import common.config.const as const
from common.config.config import config
from common.utils.utils import clone_repo, read_file_util, get_repository_name
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService


class ApplicationEditorService(BaseWorkflowService):
    """
    Service responsible for editing existing applications including
    API editing, workflow editing, processor editing, and feature additions.
    """

    async def edit_existing_app_design_additional_feature(self, technical_id: str, 
                                                         entity: AgenticFlowEntity, **params) -> str:
        """
        Edit existing application design to add additional features.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including user_request and git_branch
            
        Returns:
            Success message with workflow information or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["user_request"]
            )
            if not is_valid:
                return error_msg

            repository_name = get_repository_name(entity)
            git_branch_id = params.get(const.GIT_BRANCH_PARAM)
            
            # Validate branch (no modifications to main branch allowed)
            if git_branch_id and git_branch_id == "main":
                self.logger.exception("Modifications to main branch are not allowed")
                return "Modifications to main branch are not allowed"

            # Clone repository
            await clone_repo(git_branch_id=git_branch_id, repository_name=repository_name)

            # Determine API file based on repository type
            if repository_name.startswith("java"):
                filename = "src/main/java/com/java_template/controller/Controller.java"
            else:
                filename = "routes/routes.py"

            # Read API file
            app_api = await read_file_util(
                filename=filename,
                technical_id=git_branch_id,
                repository_name=repository_name
            )

            # Get entities description
            entities_description = []
            project_entities_list = await self.get_entities_list(
                branch_id=git_branch_id,
                repository_name=repository_name
            )

            for project_entity in project_entities_list:
                if repository_name.startswith("java"):
                    workflow_filename = f"src/main/java/com/java_template/entity/{project_entity}/Workflow.java"
                else:
                    workflow_filename = f"entity/{project_entity}/workflow.py"
                    
                workflow_code = await read_file_util(
                    technical_id=git_branch_id,
                    filename=workflow_filename,
                    repository_name=repository_name
                )
                entities_description.append({project_entity: workflow_code})

            # Prepare workflow cache
            workflow_cache = {
                'user_request': params.get("user_request")
            }

            # Store app API in edge messages
            app_api_id = await self.entity_service.add_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                entity_version=config.ENTITY_VERSION,
                entity=app_api,
                meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )

            # Store entities description in edge messages
            entities_description_id = await self.entity_service.add_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                entity_version=config.ENTITY_VERSION,
                entity=json.dumps(entities_description),
                meta={"type": config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )

            edge_messages_store = {
                'app_api': app_api_id,
                'entities_description': entities_description_id,
            }

            # Launch agentic workflow
            child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=const.ModelName.ADD_NEW_FEATURE.value,
                workflow_cache=workflow_cache,
                edge_messages_store=edge_messages_store
            )

            return (f"Successfully scheduled workflow for updating user application {child_technical_id}. "
                   f"I'll be right back - please don't ask anything else.")
                   
        except Exception as e:
            return self._handle_error(entity, e, f"Error editing application design: {e}")

    async def edit_api_existing_app(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Edit API of existing application.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including programming_language
            
        Returns:
            Success message with workflow information or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["programming_language"]
            )
            if not is_valid:
                return error_msg

            programming_language = params.get("programming_language")

            # Determine workflow name based on programming language
            workflow_name = (
                const.ModelName.EDIT_API_EXISTING_APP_JAVA.value 
                if programming_language == "JAVA" 
                else const.ModelName.EDIT_API_EXISTING_APP_PYTHON.value
            )

            return await self._schedule_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=workflow_name,
                params=params,
                resolve_entity_name=False,
            )
            
        except Exception as e:
            return self._handle_error(entity, e, f"Error editing API: {e}")

    async def edit_existing_workflow(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Edit existing workflow.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including programming_language
            
        Returns:
            Success message with workflow information or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["programming_language"]
            )
            if not is_valid:
                return error_msg

            programming_language = params.get("programming_language")

            # Determine workflow name based on programming language
            workflow_name = (
                const.ModelName.EDIT_EXISTING_WORKFLOW_JAVA.value 
                if programming_language == "JAVA" 
                else const.ModelName.EDIT_EXISTING_WORKFLOW_PYTHON.value
            )

            return await self._schedule_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=workflow_name,
                params=params,
                resolve_entity_name=True,
            )
            
        except Exception as e:
            return self._handle_error(entity, e, f"Error editing workflow: {e}")

    async def edit_existing_processors(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Edit existing processors.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including programming_language
            
        Returns:
            Success message with workflow information or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["programming_language"]
            )
            if not is_valid:
                return error_msg

            programming_language = params.get("programming_language")

            # Determine workflow name based on programming language
            workflow_name = (
                const.ModelName.EDIT_EXISTING_PROCESSORS_JAVA.value 
                if programming_language == "JAVA" 
                else const.ModelName.EDIT_EXISTING_PROCESSORS_PYTHON.value
            )

            return await self._schedule_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=workflow_name,
                params=params,
                resolve_entity_name=True,
            )
            
        except Exception as e:
            return self._handle_error(entity, e, f"Error editing processors: {e}")

    async def add_new_entity_for_existing_app(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Add new entity for existing application.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including programming_language
            
        Returns:
            Success message with workflow information or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["programming_language"]
            )
            if not is_valid:
                return error_msg

            programming_language = params.get("programming_language")

            # Determine workflow name based on programming language
            workflow_name = (
                const.ModelName.ADD_NEW_ENTITY_JAVA.value 
                if programming_language == "JAVA" 
                else const.ModelName.ADD_NEW_ENTITY_PYTHON.value
            )

            return await self._schedule_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=workflow_name,
                params=params,
            )
            
        except Exception as e:
            return self._handle_error(entity, e, f"Error adding new entity: {e}")

    async def add_new_workflow(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Add new workflow to existing application.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including programming_language
            
        Returns:
            Success message with workflow information or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["programming_language"]
            )
            if not is_valid:
                return error_msg

            programming_language = params.get("programming_language")

            # Determine workflow name based on programming language
            workflow_name = (
                const.ModelName.ADD_NEW_WORKFLOW_JAVA.value 
                if programming_language == "JAVA" 
                else const.ModelName.ADD_NEW_WORKFLOW_PYTHON.value
            )

            return await self._schedule_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=workflow_name,
                params=params,
                resolve_entity_name=True,
            )
            
        except Exception as e:
            return self._handle_error(entity, e, f"Error adding new workflow: {e}")

    async def _schedule_workflow(self, technical_id: str, entity: AgenticFlowEntity, 
                                entity_model: str, workflow_name: str, params: dict,
                                resolve_entity_name: bool = False) -> str:
        """
        Internal method to schedule workflow operations.
        This is a simplified version that delegates to the application builder service.
        """
        # This would ideally be shared or moved to a common base class
        # For now, we'll implement a basic version
        child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
            technical_id=technical_id,
            entity=entity,
            entity_model=entity_model,
            workflow_name=workflow_name,
            workflow_cache=params,
            edge_messages_store={},
        )

        return (f"Successfully scheduled workflow to implement the task. I'll be right back with a new "
               f"dialogue plan. Please don't ask anything just yet i'm back.{child_technical_id}")


