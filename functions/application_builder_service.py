import json
from typing import Any, List

import common.config.const as const
from common.config.config import config
from common.utils.utils import clone_repo
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from functions.base_service import BaseWorkflowService
from functions.repository_resolver import resolve_repository_name_with_language_param


class WorkflowNameResolver:
    """
    Resolver for determining workflow names based on programming language.
    Follows the same pattern as repository resolver for consistency.
    """

    @staticmethod
    def resolve_general_app_workflow_name(programming_language: str, type: str = "build", mode: str = "optimized", has_files: bool = False) -> str:
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
                workflow = const.ModelName.GEN_APP_ENTITY_JAVA.value
                if mode == "optimized" or has_files:
                    workflow = const.ModelName.GEN_APP_ENTITY_JAVA_OPTIMIZED.value
                return workflow
            if type == "edit":
                return const.ModelName.EDIT_GENERAL_APPLICATION_JAVA.value
        else:
            if type == "build":
                workflow = const.ModelName.GEN_APP_ENTITY_PYTHON.value
                if mode == "optimized" or has_files:
                    workflow = const.ModelName.GEN_APP_ENTITY_PYTHON_OPTIMIZED.value
                return workflow
            if type == "edit":
                return const.ModelName.EDIT_GENERAL_APPLICATION_PYTHON.value

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
            **params: Parameters including:
                - user_request: User's request
                - programming_language: Programming language
                - mode: Build mode
                - installation_id: (Optional) GitHub App installation ID for private repos
                - repository_url: (Optional) Custom repository URL for private repos

        Returns:
            Success message with workflow information or error message
        """
        try:
            # Log all received parameters
            self.logger.info("=" * 80)
            self.logger.info("build_general_application called")
            self.logger.info("=" * 80)
            self.logger.info(f"technical_id: {technical_id}")
            self.logger.info(f"entity.technical_id: {entity.technical_id}")
            self.logger.info(f"entity.workflow_name: {entity.workflow_name}")
            self.logger.info("Received parameters:")
            for key, value in params.items():
                # Mask sensitive data but show structure
                if key in ["user_request"]:
                    self.logger.info(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")
                else:
                    self.logger.info(f"  {key}: {value}")
            self.logger.info("=" * 80)

            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["user_request", "programming_language", "mode"]
            )
            if not is_valid:
                self.logger.error(f"Parameter validation failed: {error_msg}")
                return error_msg

            user_request = params.get("user_request")
            programming_language = params.get("programming_language")
            installation_id = params.get("installation_id")
            repository_url = params.get("repository_url")

            # If no installation_id/repository_url provided, use public repo configuration
            if not installation_id and not repository_url:
                # Use public repository configuration from .env
                installation_id = config.GITHUB_PUBLIC_REPO_INSTALLATION_ID

                # Select repository URL based on programming language
                if programming_language.lower() == "python":
                    repository_url = config.PYTHON_PUBLIC_REPO_URL
                elif programming_language.lower() == "java":
                    repository_url = config.JAVA_PUBLIC_REPO_URL

                self.logger.info("Using public repository configuration from .env:")
                self.logger.info(f"  Programming language: {programming_language}")
                self.logger.info(f"  Installation ID: {installation_id}")
                self.logger.info(f"  Repository URL: {repository_url}")
            else:
                self.logger.info("Using user-provided private repository configuration:")
                self.logger.info(f"  Installation ID: {installation_id}")
                self.logger.info(f"  Repository URL: {repository_url}")

            # Collect all file edge message IDs from chat history
            file_edge_message_ids = self._collect_file_edge_message_ids(entity)

            # Add file edge message IDs to workflow cache
            if file_edge_message_ids:
                params["file_edge_message_ids"] = file_edge_message_ids

            # Store programming_language in workflow_cache (already in params)
            params[const.PROGRAMMING_LANGUAGE_PARAM] = programming_language

            # Calculate and store repository_name in workflow_cache
            # IMPORTANT: Always use environment variable name (JAVA_REPOSITORY_NAME or PYTHON_REPOSITORY_NAME)
            # as the directory name, regardless of the actual repository name in the URL.
            # This ensures consistent directory naming for scripts that reference the cloned directory.
            repository_name = resolve_repository_name_with_language_param(entity, programming_language)

            if repository_url:
                params[const.REPOSITORY_URL_PARAM] = repository_url

            params[const.REPOSITORY_NAME_PARAM] = repository_name

            # Store installation_id if provided
            if installation_id:
                params[const.INSTALLATION_ID_PARAM] = installation_id

            # Determine workflow name based on programming language
            workflow_name = WorkflowNameResolver.resolve_general_app_workflow_name(programming_language=programming_language,
                                                                                   mode=params.get("mode"),
                                                                                   has_files=bool(file_edge_message_ids))

            # Save params to current entity's workflow_cache for context
            entity.workflow_cache.update(params)

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

            entity.workflow_cache[const.CURRENT_CHAT_GITHUB_BRANCH] = child_technical_id
            entity.workflow_cache[const.CURRENT_CHAT_ALLOWED_GITHUB_BRANCH] = child_technical_id


            return (f"Workflow {workflow_name} {child_technical_id} has been scheduled successfully. "
                   f"You'll be notified when it is in progress.")

        except Exception as e:
            return self._handle_error(entity, e, f"Error building general application: {e}")


    async def edit_general_application(self, technical_id: str, entity: ChatEntity, **params: Any) -> str:
        """
        Edit an existing application based on user request and programming language.

        Args:
            technical_id: Technical identifier
            entity: Chat entity
            **params: Parameters including:
                - user_request: User's edit/update request
                - git_branch: Git branch where the application exists
                - programming_language: Programming language (JAVA or PYTHON)
                - repository_type: (Optional) "public" or "private" - determines repo configuration
                - installation_id: (Optional) GitHub App installation ID for private repos
                - repository_url: (Optional) Repository URL for private repos

        Returns:
            Success message with workflow information or error message
        """
        try:
            # Log all received parameters
            self.logger.info("=" * 80)
            self.logger.info("edit_general_application called")
            self.logger.info("=" * 80)
            self.logger.info(f"technical_id: {technical_id}")
            self.logger.info(f"entity.technical_id: {entity.technical_id}")
            self.logger.info(f"entity.workflow_name: {entity.workflow_name}")
            self.logger.info("Received parameters:")
            for key, value in params.items():
                # Mask sensitive data but show structure
                if key in ["user_request"]:
                    self.logger.info(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")
                else:
                    self.logger.info(f"  {key}: {value}")
            self.logger.info("=" * 80)

            # Validate required parameters
            is_valid, error_msg = await self._validate_required_params(
                params, ["user_request", "programming_language", "git_branch"]
            )
            if not is_valid:
                self.logger.error(f"Parameter validation failed: {error_msg}")
                return error_msg

            if entity.user_id.startswith("guest_"):
                return "Editing applications is not supported for guest users. Please sign up for a free account and continue in a newchat. You will need to start a new chat to continue."

            user_request = params.get("user_request")
            programming_language = params.get("programming_language")
            git_branch = params.get("git_branch")
            repository_type = params.get("repository_type", "").lower()
            installation_id = params.get("installation_id")
            repository_url = params.get("repository_url")

            # Validate git branch (prevent main branch modifications)
            if git_branch == "main":
                self.logger.error("Modifications to main branch are not allowed")
                return "Modifications to main branch are not allowed"

            # Validate repository_type if provided
            if repository_type and repository_type not in ["public", "private"]:
                error_msg = f"Invalid repository_type '{repository_type}'. Must be 'public' or 'private'."
                self.logger.error(error_msg)
                return error_msg

            # If repository_type is "private", validate that installation_id and repository_url are provided
            if repository_type == "private":
                if not installation_id or not repository_url:
                    error_msg = "For private repositories, both 'installation_id' and 'repository_url' are required."
                    self.logger.error(error_msg)
                    return error_msg
                self.logger.info("Using private repository configuration:")
                self.logger.info(f"  Programming language: {programming_language}")
                self.logger.info(f"  Git branch: {git_branch}")
                self.logger.info(f"  Installation ID: {installation_id}")
                self.logger.info(f"  Repository URL: {repository_url}")
            # If no installation_id/repository_url provided OR repository_type is "public", use public repo configuration
            elif not installation_id and not repository_url:
                # Use public repository configuration from .env
                installation_id = config.GITHUB_PUBLIC_REPO_INSTALLATION_ID

                # Select repository URL based on programming language
                if programming_language.lower() == "python":
                    repository_url = config.PYTHON_PUBLIC_REPO_URL
                elif programming_language.lower() == "java":
                    repository_url = config.JAVA_PUBLIC_REPO_URL

                self.logger.info("Using public repository configuration from .env:")
                self.logger.info(f"  Programming language: {programming_language}")
                self.logger.info(f"  Git branch: {git_branch}")
                self.logger.info(f"  Installation ID: {installation_id}")
                self.logger.info(f"  Repository URL: {repository_url}")

            # Collect all file edge message IDs from chat history
            file_edge_message_ids = self._collect_file_edge_message_ids(entity)

            # Add file edge message IDs to workflow cache
            if file_edge_message_ids:
                params["file_edge_message_ids"] = file_edge_message_ids

            # Store programming_language in workflow_cache (already in params)
            params[const.PROGRAMMING_LANGUAGE_PARAM] = programming_language

            # Store git_branch in workflow_cache
            params[const.GIT_BRANCH_PARAM] = git_branch

            # Calculate and store repository_name in workflow_cache
            # IMPORTANT: Always use environment variable name (JAVA_REPOSITORY_NAME or PYTHON_REPOSITORY_NAME)
            # as the directory name, regardless of the actual repository name in the URL.
            # This ensures consistent directory naming for scripts that reference the cloned directory.
            repository_name = resolve_repository_name_with_language_param(entity, programming_language)
            params[const.REPOSITORY_NAME_PARAM] = repository_name

            # Store repository_url in workflow_cache
            params[const.REPOSITORY_URL_PARAM] = repository_url

            # Store installation_id in workflow_cache
            params[const.INSTALLATION_ID_PARAM] = installation_id

            # Determine workflow name based on programming language
            workflow_name = WorkflowNameResolver.resolve_general_app_workflow_name(
                programming_language=programming_language,
                type="edit"
            )

            # Save params to current entity's workflow_cache for context
            entity.workflow_cache.update(params)

            # Launch agentic workflow
            child_technical_id = await self.workflow_helper_service.launch_agentic_workflow(
                technical_id=technical_id,
                entity=entity,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                workflow_name=workflow_name,
                user_request=user_request,
                workflow_cache=params,
                resume_transition=None
            )

            return (f"Workflow {workflow_name} {child_technical_id} has been scheduled successfully. "
                    f"You'll be notified when it is in progress.")

        except Exception as e:
            return self._handle_error(entity, e, f"Error editing general application: {e}")

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
            installation_id = params.get(const.INSTALLATION_ID_PARAM, entity.workflow_cache.get(const.INSTALLATION_ID_PARAM))
            repository_url = params.get(const.REPOSITORY_URL_PARAM, entity.workflow_cache.get(const.REPOSITORY_URL_PARAM))

            # Get repository_name from cache or calculate it
            # IMPORTANT: Always use environment variable name (JAVA_REPOSITORY_NAME or PYTHON_REPOSITORY_NAME)
            # as the directory name, regardless of the actual repository name in the URL.
            # This ensures consistent directory naming for scripts that reference the cloned directory.
            repository_name = entity.workflow_cache.get(const.REPOSITORY_NAME_PARAM)
            if not repository_name:
                repository_name = resolve_repository_name_with_language_param(entity, programming_language)

            # Validate branch (no modifications to main branch allowed)
            if git_branch_id and git_branch_id == "main":
                self.logger.exception("Modifications to main branch are not allowed")
                return "Modifications to main branch are not allowed"

            # Determine workflow name based on programming language
            workflow_name = WorkflowNameResolver.resolve_general_app_workflow_name(programming_language)

            # Clone repository if branch ID provided
            if git_branch_id:
                await clone_repo(
                    git_branch_id=git_branch_id,
                    repository_name=repository_name,
                    installation_id=installation_id,
                    repository_url=repository_url
                )

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
            # Get parameters from cache if not provided
            if const.REPOSITORY_NAME_PARAM not in params:
                params[const.REPOSITORY_NAME_PARAM] = entity.workflow_cache.get(const.REPOSITORY_NAME_PARAM)
            if const.GIT_BRANCH_PARAM not in params:
                params[const.GIT_BRANCH_PARAM] = entity.workflow_cache.get(const.GIT_BRANCH_PARAM)
            if const.PROGRAMMING_LANGUAGE_PARAM not in params:
                params[const.PROGRAMMING_LANGUAGE_PARAM] = entity.workflow_cache.get(const.PROGRAMMING_LANGUAGE_PARAM)

            # Validate required parameters
            programming_language = params.get(const.PROGRAMMING_LANGUAGE_PARAM)
            if not programming_language:
                return "Missing required parameters: programming_language"

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
            # Get repository_name from cache or calculate it
            repository_name = entity.workflow_cache.get(const.REPOSITORY_NAME_PARAM)
            if not repository_name:
                repository_name = resolve_repository_name_with_language_param(entity)

            git_branch_id: str = params.get(const.GIT_BRANCH_PARAM, entity.workflow_cache.get(const.GIT_BRANCH_PARAM))
            installation_id = params.get(const.INSTALLATION_ID_PARAM, entity.workflow_cache.get(const.INSTALLATION_ID_PARAM))
            repository_url = params.get(const.REPOSITORY_URL_PARAM, entity.workflow_cache.get(const.REPOSITORY_URL_PARAM))

            if git_branch_id:
                if git_branch_id == "main":
                    self.logger.exception("Modifications to main branch are not allowed")
                    return "Modifications to main branch are not allowed"
                await clone_repo(
                    git_branch_id=git_branch_id,
                    repository_name=repository_name,
                    installation_id=installation_id,
                    repository_url=repository_url
                )

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

    def _collect_file_edge_message_ids(self, entity: ChatEntity) -> List[str]:
        """
        Collect all file edge message IDs from the chat history.

        Args:
            entity: Chat entity containing chat flow with messages

        Returns:
            List of file edge message IDs found in the conversation
        """
        file_edge_message_ids = []

        # Process current flow messages
        if entity.chat_flow and entity.chat_flow.current_flow:
            for message in entity.chat_flow.current_flow:
                file_ids = self._extract_file_ids_from_message(message)
                file_edge_message_ids.extend(file_ids)

        # Process finished flow messages
        if entity.chat_flow and entity.chat_flow.finished_flow:
            for message in entity.chat_flow.finished_flow:
                file_ids = self._extract_file_ids_from_message(message)
                file_edge_message_ids.extend(file_ids)

        # Remove duplicates while preserving order
        unique_file_ids = []
        seen = set()
        for file_id in file_edge_message_ids:
            if file_id not in seen:
                unique_file_ids.append(file_id)
                seen.add(file_id)

        return unique_file_ids

    def _extract_file_ids_from_message(self, message) -> List[str]:
        """
        Extract file IDs from a single FlowEdgeMessage.

        Args:
            message: FlowEdgeMessage object

        Returns:
            List of file IDs found in the message
        """
        file_ids = []

        # Check for file blob IDs
        if hasattr(message, 'file_blob_ids') and message.file_blob_ids:
            file_ids.extend(message.file_blob_ids)

        return file_ids

