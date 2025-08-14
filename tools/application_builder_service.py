import json
from typing import Any

import common.config.const as const
from common.config.config import config
from common.utils.utils import clone_repo
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from tools.base_service import BaseWorkflowService
from tools.repository_resolver import resolve_repository_name_with_language_param


class WorkflowNameResolver:
    """
    Resolver for determining workflow names based on programming language.
    Follows the same pattern as repository resolver for consistency.
    """

    @staticmethod
    def resolve_general_app_workflow_name(programming_language: str, type: str = "build") -> str:
        """
        Resolve general application workflow name based on programming language.

        Args:
            programming_language: Programming language (case-insensitive)

        Returns:
            Workflow name for the language
            :param type:
        """
        language_upper = programming_language.upper()

        if language_upper == "JAVA":
            if type == "build":
                return const.ModelName.GEN_APP_ENTITY_JAVA.value
            if type == "edit":
                return const.ModelName.EDIT_GEN_APP_ENTITY_JAVA.value
        else:
            if type == "build":
                return const.ModelName.GEN_APP_ENTITY_PYTHON.value

    @staticmethod
    def resolve_setup_workflow_name(programming_language: str) -> str:
        """
        Resolve setup workflow name based on programming language.

        Args:
            programming_language: Programming language (case-insensitive)

        Returns:
            Setup workflow name for the language
        """
        language_upper = programming_language.upper()

        if language_upper == "JAVA":
            return const.ModelName.INIT_SETUP_WORKFLOW_JAVA.value
        else:
            return const.ModelName.INIT_SETUP_WORKFLOW_PYTHON.value


class ApplicationBuilderService(BaseWorkflowService):
    """
    Service responsible for building new applications including
    general application building, setup workflows, and initialization.
    """

    async def build_general_application(self, technical_id: str, entity: ChatEntity, **params: Any) -> str:
        """
        Build a general application based on user request and programming language.
        
        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including user_request and programming_language
            
        Returns:
            Success message with workflow information or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["user_request", "programming_language"]
            )
            if not is_valid:
                return error_msg

            user_request = params.get("user_request")
            programming_language = params.get("programming_language")

            # Determine workflow name based on programming language
            workflow_name = WorkflowNameResolver.resolve_general_app_workflow_name(programming_language)

            # Launch agentic workflow
            child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=workflow_name,
                user_request=user_request,
                workflow_cache=params,
                resume_transition=const.TransitionKey.BUILD_NEW_APP.value
            )

            return (f"Workflow {workflow_name} {child_technical_id} has been scheduled successfully. "
                   f"You'll be notified when it is in progress.")
                   
        except Exception as e:
            return self._handle_error(entity, e, f"Error building general application: {e}")


    async def edit_general_application_java(self, technical_id: str, entity: ChatEntity, **params: Any) -> str:
        """
        Build a general application based on user request and programming language.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including user_request and programming_language

        Returns:
            Success message with workflow information or error message
        """
        try:
            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["user_request", "programming_language", "git_branch"]
            )
            if not is_valid:
                return error_msg

            user_request = params.get("user_request")
            programming_language = params.get("programming_language")

            # Determine workflow name based on programming language
            workflow_name = WorkflowNameResolver.resolve_general_app_workflow_name(programming_language=programming_language,
                                                                                   type="edit")

            # Launch agentic workflow
            child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=workflow_name,
                workflow_cache=params
            )

            return (f"Workflow {workflow_name} {child_technical_id} has been scheduled successfully. "
                    f"You'll be notified when it is in progress.")

        except Exception as e:
            return self._handle_error(entity, e, f"Error building general application: {e}")

    async def resume_build_general_application(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Resume building a general application from a specific transition.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            **params: Parameters including programming_language, git_branch, and transition
            
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
            git_branch_id = params.get(const.GIT_BRANCH_PARAM)
            transition = params.get("transition")

            # Determine repository name based on programming language
            repository_name = resolve_repository_name_with_language_param(entity, programming_language)

            # Validate branch (no modifications to main branch allowed)
            if git_branch_id and git_branch_id == "main":
                self.logger.exception("Modifications to main branch are not allowed")
                return "Modifications to main branch are not allowed"

            # Determine workflow name based on programming language
            workflow_name = WorkflowNameResolver.resolve_general_app_workflow_name(programming_language)

            # Clone repository if branch ID provided
            if git_branch_id:
                await clone_repo(git_branch_id=git_branch_id, repository_name=repository_name)

            # Launch agentic workflow
            child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=workflow_name,
                workflow_cache=params,
                resume_transition=transition,
                edge_messages_store=None
            )

            return (f"Successfully scheduled workflow for updating user application {child_technical_id}. "
                   f"I'll be right back - please don't ask anything else.")
                   
        except Exception as e:
            return self._handle_error(entity, e, f"Error resuming application build: {e}")

    async def init_setup_workflow(self, technical_id: str, entity: AgenticFlowEntity, **params) -> str:
        """
        Initialize setup workflow for application setup.
        
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
            params[const.REPOSITORY_NAME_PARAM] = entity.workflow_cache.get(const.REPOSITORY_NAME_PARAM)
            params[const.GIT_BRANCH_PARAM] = entity.workflow_cache.get(const.GIT_BRANCH_PARAM)

            # Determine workflow name based on programming language
            workflow_name = WorkflowNameResolver.resolve_setup_workflow_name(programming_language)

            return await self._schedule_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=workflow_name,
                params=params,
            )
            
        except Exception as e:
            return self._handle_error(entity, e, f"Error initializing setup workflow: {e}")

    async def _schedule_workflow(self, technical_id: str, entity: AgenticFlowEntity, 
                                entity_model: str, workflow_name: str, params: dict,
                                resolve_entity_name: bool = False) -> str:
        """
        Internal method to schedule workflow operations with repository cloning and entity resolution.
        
        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            entity_model: Entity model name
            workflow_name: Workflow name
            params: Parameters for the workflow
            resolve_entity_name: Whether to resolve entity name
            
        Returns:
            Success message with workflow information or error message
        """
        try:
            # Clone the repo based on branch ID if provided
            repository_name = resolve_repository_name_with_language_param(entity)
            git_branch_id: str = params.get(const.GIT_BRANCH_PARAM, entity.workflow_cache.get(const.GIT_BRANCH_PARAM))
            
            if git_branch_id:
                if git_branch_id == "main":
                    self.logger.exception("Modifications to main branch are not allowed")
                    return "Modifications to main branch are not allowed"
                await clone_repo(git_branch_id=git_branch_id, repository_name=repository_name)

            # One-off resolution for workflows that need an entity_name
            if resolve_entity_name:
                entity_name = await self.resolve_entity_name(
                    entity_name=params.get("entity_name"),
                    branch_id=git_branch_id,
                    repository_name=repository_name
                )
                params["entity_name"] = entity_name

            # Launch the actual agentic workflow
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
                   
        except Exception as e:
            return self._handle_error(entity, e, f"Error scheduling workflow: {e}")


