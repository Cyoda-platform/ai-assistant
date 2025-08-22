import asyncio
import logging
import os
from typing import Dict, Any, List
import aiofiles
import common.config.const as const
from common.config.config import config as env_config
from common.utils.utils import save_all, clone_repo, generate_uuid
from entity.model import AgenticFlowEntity, ChatMemory, ModelConfig, AIMessage
from workflow.config_builder import ConfigBuilder

logger = logging.getLogger(__name__)


class JobsProcessor:
    """
    Handles processing of jobs configurations with split functions, input files, and file generation.
    """

    def __init__(self, ai_agent, method_registry, memory_manager, cls_instance, 
                 entity_service, cyoda_auth_service, config_builder=None):
        """
        Initialize the jobs processor.

        Args:
            ai_agent: AI agent instance
            method_registry: Method registry for function calling
            memory_manager: Memory manager for chat operations
            cls_instance: Class instance for AI agent function calling
            entity_service: Entity service for edge message handling
            cyoda_auth_service: Cyoda auth service
            config_builder: Optional ConfigBuilder instance for message resolution
        """
        self.ai_agent = ai_agent
        self.method_registry = method_registry
        self.memory_manager = memory_manager
        self.cls_instance = cls_instance
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
        self.config_builder = config_builder or ConfigBuilder()

    async def process_jobs(self, config: Dict[str, Any], entity: AgenticFlowEntity, 
                          memory: ChatMemory, technical_id: str) -> str:
        """
        Process jobs configuration with split functions and file generation.

        Args:
            config: Configuration with jobs
            entity: Agentic flow entity
            memory: Chat memory
            technical_id: Technical identifier

        Returns:
            Response string with generated file paths or error message
        """
        try:
            jobs = config.get("jobs", [])
            responses = []
            # Get memory tags once for jobs path
            memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])

            # Create async tasks for all jobs and values
            async_tasks = []

            for job in jobs:
                split_function = job.get("split_function")
                split_parameter = split_function.get("split_parameter")
                split_function_name = split_function.get("name")

                # Execute split function to get entity values
                values = await self.method_registry.methods_dict[split_function_name](
                    self.cls_instance, technical_id=technical_id, entity=entity, params=split_function
                )
                if not values:
                    logger.warning(f"No values returned from split function: {split_function_name}")
                    continue  # Skip this job if no values returned

                # Create async tasks for all values in this job
                for value in values:
                    task = self._process_job_for_entity(job, value, split_parameter, config, entity, technical_id)
                    async_tasks.append(task)

            # Execute all tasks concurrently
            if async_tasks:
                task_results = await asyncio.gather(*async_tasks, return_exceptions=True)

                # Filter successful responses and log errors
                for result in task_results:
                    if isinstance(result, Exception):
                        logger.error(f"Task failed with exception: {result}")
                    elif result is not None:
                        responses.append(result)

            # Save all files and perform single git push
            response = await self._save_and_commit_responses(responses, jobs, entity)

            return response
            
        except Exception as e:
            logger.exception(f"Error in jobs processing: {e}")
            return f"Sorry, i'm having a little trouble with the LLM: usually it's ok, just send a message 'retry' to retry or go to the next step ('proceed' or click approve)."

    async def _process_job_for_entity(self, job: Dict[str, Any], entity_value: str, split_parameter: str,
                                    config: Dict[str, Any], entity: AgenticFlowEntity, technical_id: str) -> Dict[str, Any]:
        """
        Process a single job for a specific entity value.

        Args:
            job: Job configuration
            entity_value: The entity value (e.g., "User", "Product")
            split_parameter: The parameter name to replace (e.g., "EntityName")
            config: Parent configuration
            entity: Agentic flow entity
            technical_id: Technical identifier

        Returns:
            Dictionary with output_path and data, or None if processing failed
        """
        try:
            # Get model configuration
            model = ModelConfig.model_validate(config.get("model", {}))
            job_config = job.copy()
            
            # Resolve message references using ConfigBuilder
            raw_messages = job_config.get("messages", [])
            resolved_messages = self.config_builder._resolve_message_references(raw_messages)

            # Convert to AIMessage objects and append input file contents
            messages = await self._build_messages_with_input_files(resolved_messages, job_config, entity, split_parameter, entity_value)
            
            # Run the AI agent
            value_response = await self.ai_agent.run_agent(
                methods_dict=self.method_registry.methods_dict,
                technical_id=technical_id,
                cls_instance=self.cls_instance,
                entity=entity,
                tools=job_config.get("tools"),
                model=model,
                messages=messages,
                tool_choice=job_config.get("tool_choice"),
                response_format=job_config.get("response_format")
            )
            
            # Format the output path with the actual entity value
            output_path = job.get("output")

            # Replace all possible parameter variations in the output path
            format_params = {
                split_parameter: entity_value,  # Original parameter (e.g., EntityName -> User)
                split_parameter.lower(): entity_value.lower()     # Backwards compatibility for EntityName   # All lowercase for entityname
            }

            output_path = output_path.format(**format_params)

            return {"output_path": output_path, "data": value_response}
            
        except Exception as e:
            logger.exception(f"Error processing job for entity {entity_value}: {e}")
            return None

    async def _build_messages_with_input_files(self, resolved_messages: List[Dict[str, Any]], 
                                             job_config: Dict[str, Any], entity: AgenticFlowEntity, split_parameter: str, entity_value: str) -> List[AIMessage]:
        """
        Build AIMessage objects from resolved messages and append input file contents.

        Args:
            resolved_messages: Messages resolved by ConfigBuilder
            job_config: Job configuration containing input files
            entity: Agentic flow entity for repository context

        Returns:
            List of AIMessage objects with input file contents appended
        """
        messages = []
        
        # Convert resolved messages to AIMessage objects
        for message in resolved_messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            # Handle content as list (backwards compatibility)
            if isinstance(content, list):
                content = "\n".join(str(c) for c in content)

            # Format content with entity value - replace {split_parameter_value} with actual entity value
            if content and "{split_parameter_value}" in content:
                content = content.replace("{split_parameter_value}", entity_value)

            if content and "{split_parameter_value_lower}" in content:
                content = content.replace("{split_parameter_value_lower}", entity_value.lower())

            if content and "{split_parameter_value_upper}" in content:
                content = content.replace("{split_parameter_value_upper}", entity_value.upper())

            messages.append(AIMessage(role=role, content=content))

        # Append input file contents if specified
        input_config = job_config.get("input", {})
        local_fs_files = input_config.get("local_fs", [])

        if local_fs_files:
            input_contents, actual_files = await self._read_input_files_with_paths(local_fs_files, entity)
            if input_contents:
                # Show both the specified paths and actual files read
                paths_info = f"Specified paths: {', '.join(local_fs_files)}"
                if actual_files != local_fs_files:
                    paths_info += f"\nActual files read: {', '.join(actual_files)}"

                # Append input file contents as a system message with file paths included
                input_message = AIMessage(
                    role="system",
                    content=f"Input files content ({paths_info}):\n\n{input_contents}"
                )
                messages.append(input_message)

        return messages

    def _get_git_branch_id(self, entity: AgenticFlowEntity) -> str:
        """
        Get git branch ID from entity workflow cache.

        Args:
            entity: Agentic flow entity

        Returns:
            Git branch ID or None if not found
        """
        return entity.workflow_cache.get(const.GIT_BRANCH_PARAM)

    def _get_repository_name(self, entity: AgenticFlowEntity) -> str:
        """
        Get repository name for the entity.

        Args:
            entity: Agentic flow entity

        Returns:
            Repository name
        """
        from common.utils.utils import get_repository_name
        return get_repository_name(entity)

    async def _read_input_files(self, file_paths: List[str], entity: AgenticFlowEntity) -> str:
        """
        Read contents from input files and directories specified in the job configuration.
        For directories, recursively reads all files in subdirectories.

        Args:
            file_paths: List of file or directory paths to read
            entity: Agentic flow entity for repository context

        Returns:
            Combined contents of all input files with their full paths
        """
        try:
            # Clone repository to read files
            branch_id = self._get_git_branch_id(entity)
            repository_name = self._get_repository_name(entity)

            if not branch_id or not repository_name:
                logger.warning("Missing branch_id or repository_name for reading input files")
                return ""

            await clone_repo(git_branch_id=branch_id, repository_name=repository_name)
            from common.config.config import config
            clone_dir = f"{config.PROJECT_DIR}/{branch_id}/{repository_name}"

            file_contents = []

            for path in file_paths:
                try:
                    full_path = os.path.join(clone_dir, path)

                    if os.path.isfile(full_path):
                        # Handle single file
                        content = await self._read_single_file(full_path, path)
                        file_contents.append(content)
                    elif os.path.isdir(full_path):
                        # Handle directory - recursively read all files
                        dir_contents = await self._read_directory_files(full_path, path, clone_dir)
                        file_contents.extend(dir_contents)
                    else:
                        logger.warning(f"Input path not found: {path}")
                        file_contents.append(f"=== {path} ===\n[Path not found]")

                except Exception as e:
                    logger.error(f"Error processing input path {path}: {e}")
                    file_contents.append(f"=== {path} ===\n[Error processing path: {e}]")

            return "\n\n".join(file_contents)

        except Exception as e:
            logger.exception(f"Error reading input files: {e}")
            return ""

    async def _read_input_files_with_paths(self, file_paths: List[str], entity: AgenticFlowEntity) -> tuple[str, List[str]]:
        """
        Read contents from input files and directories, returning both content and actual file paths.

        Args:
            file_paths: List of file or directory paths to read
            entity: Agentic flow entity for repository context

        Returns:
            Tuple of (combined contents, list of actual file paths read)
        """
        try:
            # Clone repository to read files
            branch_id = self._get_git_branch_id(entity)
            repository_name = self._get_repository_name(entity)

            if not branch_id or not repository_name:
                logger.warning("Missing branch_id or repository_name for reading input files")
                return "", []

            await clone_repo(git_branch_id=branch_id, repository_name=repository_name)
            from common.config.config import config
            clone_dir = f"{config.PROJECT_DIR}/{branch_id}/{repository_name}"

            file_contents = []
            actual_files = []

            for path in file_paths:
                try:
                    full_path = os.path.join(clone_dir, path)

                    if os.path.isfile(full_path):
                        # Handle single file
                        content = await self._read_single_file(full_path, path)
                        file_contents.append(content)
                        actual_files.append(path)
                    elif os.path.isdir(full_path):
                        # Handle directory - recursively read all files
                        dir_contents, dir_files = await self._read_directory_files_with_paths(full_path, path, clone_dir)
                        file_contents.extend(dir_contents)
                        actual_files.extend(dir_files)
                    else:
                        logger.warning(f"Input path not found: {path}")
                        file_contents.append(f"=== {path} ===\n[Path not found]")
                        actual_files.append(path)

                except Exception as e:
                    logger.error(f"Error processing input path {path}: {e}")
                    file_contents.append(f"=== {path} ===\n[Error processing path: {e}]")
                    actual_files.append(path)

            return "\n\n".join(file_contents), actual_files

        except Exception as e:
            logger.exception(f"Error reading input files: {e}")
            return "", []

    async def _read_single_file(self, full_path: str, relative_path: str) -> str:
        """
        Read content from a single file.

        Args:
            full_path: Full filesystem path to the file
            relative_path: Relative path for display purposes

        Returns:
            Formatted file content with path header
        """
        try:
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                logger.info(f"Successfully read input file: {relative_path}")
                return f"=== {relative_path} ===\n{content}"
        except Exception as e:
            logger.error(f"Error reading file {relative_path}: {e}")
            return f"=== {relative_path} ===\n[Error reading file: {e}]"

    async def _read_directory_files(self, full_dir_path: str, relative_dir_path: str, clone_dir: str) -> List[str]:
        """
        Recursively read all files in a directory and its subdirectories.

        Args:
            full_dir_path: Full filesystem path to the directory
            relative_dir_path: Relative directory path for display purposes
            clone_dir: Base clone directory for calculating relative paths

        Returns:
            List of formatted file contents with their relative paths
        """
        file_contents, _ = await self._read_directory_files_with_paths(full_dir_path, relative_dir_path, clone_dir)
        return file_contents

    async def _read_directory_files_with_paths(self, full_dir_path: str, relative_dir_path: str, clone_dir: str) -> tuple[List[str], List[str]]:
        """
        Recursively read all files in a directory and its subdirectories.

        Args:
            full_dir_path: Full filesystem path to the directory
            relative_dir_path: Relative directory path for display purposes
            clone_dir: Base clone directory for calculating relative paths

        Returns:
            Tuple of (list of formatted file contents, list of relative file paths)
        """
        file_contents = []
        file_paths = []

        try:
            # Walk through directory recursively
            for root, dirs, files in os.walk(full_dir_path):
                # Filter out hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file_name in files:
                    # Skip hidden files
                    if file_name.startswith('.'):
                        continue

                    file_path = os.path.join(root, file_name)
                    # Calculate relative path from clone directory
                    relative_file_path = os.path.relpath(file_path, clone_dir)

                    try:
                        content = await self._read_single_file(file_path, relative_file_path)
                        file_contents.append(content)
                        file_paths.append(relative_file_path)
                    except Exception as e:
                        logger.error(f"Error reading file {relative_file_path}: {e}")
                        file_contents.append(f"=== {relative_file_path} ===\n[Error reading file: {e}]")
                        file_paths.append(relative_file_path)

        except Exception as e:
            logger.error(f"Error walking directory {relative_dir_path}: {e}")
            file_contents.append(f"=== {relative_dir_path} ===\n[Error reading directory: {e}]")
            file_paths.append(relative_dir_path)

        return file_contents, file_paths

    async def _save_and_commit_responses(self, responses: List[Dict[str, Any]], jobs: List[Dict[str, Any]],
                                       entity: AgenticFlowEntity) -> str:
        """
        Save all responses to files and perform a single git commit.

        Args:
            responses: List of response dictionaries with output_path and data
            jobs: List of job configurations for commit message generation
            entity: Agentic flow entity

        Returns:
            Response message indicating success or failure
        """
        if not responses:
            return "No files generated"

        try:
            branch_id = self._get_git_branch_id(entity)
            repository_name = self._get_repository_name(entity)

            if not branch_id or not repository_name:
                logger.warning("Missing branch_id or repository_name, cannot save files")
                return "Warning: Generated content but could not save files (missing repository info)"

            # Generate commit message based on job type and entity count
            entity_count = len(responses)
            job_type = jobs[0].get("split_function", {}).get("name", "job") if jobs else "job"
            commit_message = f"Generated {entity_count} files from {job_type}"

            # Save all files and perform single git push
            save_success = await save_all(
                responses=responses,
                git_branch_id=branch_id,
                repository_name=repository_name,
                commit_message=commit_message
            )

            if save_success:
                logger.info(f"Successfully saved and pushed {entity_count} files")
                # Create response with output paths for user feedback
                return "\n".join([resp["output_path"] for resp in responses])
            else:
                logger.error("Failed to save files")
                return "Error: Failed to save generated files"

        except Exception as e:
            logger.exception(f"Error saving and committing responses: {e}")
            return "Error: Failed to save generated files"
