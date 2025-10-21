import asyncio
import logging
from typing import Dict, Any, List, Optional
import common.config.const as const
from common.config.config import config as env_config
from common.utils.chat_util_functions import enrich_config_message
from common.utils.utils import get_current_timestamp_num
from entity.model import AgenticFlowEntity, ChatMemory, ModelConfig, FlowEdgeMessage, AIMessage
from workflow.config_builder import ConfigBuilder
from workflow.dispatcher.jobs_processor import JobsProcessor
from workflow.dispatcher.auggie_processor import AuggieProcessor

# Conditional import to avoid dependency issues during testing
try:
    from common.utils.batch_parallel_code import batch_process_file
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import batch_process_file: {e}")
    batch_process_file = None

logger = logging.getLogger(__name__)


class AIAgentHandler:
    """
    Handles AI agent interactions, including running agents and processing responses.
    """

    def __init__(self, ai_agent, method_registry, memory_manager, cls_instance, entity_service, cyoda_auth_service,
                 config_builder=None):
        """
        Initialize the AI agent handler.

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

        # Keep references to background tasks to prevent garbage collection
        self._background_tasks = set()

        # Initialize jobs processor
        self.jobs_processor = JobsProcessor(
            ai_agent=ai_agent,
            method_registry=method_registry,
            memory_manager=memory_manager,
            cls_instance=cls_instance,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            config_builder=self.config_builder
        )

        # Initialize auggie processor
        self.auggie_processor = AuggieProcessor(
            ai_agent=ai_agent,
            method_registry=method_registry,
            memory_manager=memory_manager,
            cls_instance=cls_instance,
            entity_service=entity_service,
            cyoda_auth_service=cyoda_auth_service,
            config_builder=self.config_builder
        )

    async def run_ai_agent(self, config: Dict[str, Any], entity: AgenticFlowEntity,
                           memory: ChatMemory, technical_id: str) -> str:
        """
        Run the AI agent with the given configuration.

        Args:
            config: AI agent configuration
            entity: Agentic flow entity
            memory: Chat memory
            technical_id: Technical identifier

        Returns:
            AI agent response
        """
        try:
            # Handle batch processing
            if config.get("type") == "batch":
                return await self._handle_batch_processing(config)

            # Check and update iteration if configured
            if self._check_and_update_iteration(config=config, entity=entity):
                return "Let's proceed to the next iteration"

            # Append configured messages to memory if present
            finished_flow = entity.chat_flow.finished_flow

            if config.get("type") == "agent" and config.get("agent_type") and config.get("agent_type") == "auggie":
                # Handle Auggie CLI processing - return immediate success and run in background
                task = asyncio.create_task(self._run_auggie_background_task(config, entity, memory, technical_id))
                self._background_tasks.add(task)
                # Remove task from set when it completes to prevent memory leaks
                task.add_done_callback(self._background_tasks.discard)
                response = "CLI process started successfully. You will be notified when it completes."
            elif not config.get("jobs"):
                await self._append_messages(entity=entity, memory=memory, config=config, finished_flow=finished_flow)
                # Get memory messages including input data
                memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])
                messages = await self._get_ai_memory(entity=entity, config=config, memory=memory,
                                                     technical_id=technical_id)
                # Extract model configuration
                model = ModelConfig.model_validate(config.get("model", {}))

                # Process file content for empty/minimal user messages
                await self._process_file_content_for_empty_messages(messages, finished_flow)

                # Run the AI agent with correct signature
                response = await self.ai_agent.run_agent(
                    methods_dict=self.method_registry.methods_dict,
                    technical_id=technical_id,
                    cls_instance=self.cls_instance,
                    entity=entity,
                    tools=config.get("tools"),
                    model=model,
                    messages=messages,
                    tool_choice=config.get("tool_choice"),
                    response_format=config.get("response_format")
                )
                await self.memory_manager.store_ai_response(response=response, memory=memory, memory_tags=memory_tags)

            elif config.get("jobs"):
                # Handle jobs processing using dedicated processor
                response = await self.jobs_processor.process_jobs(config, entity, memory, technical_id)

            else:
                # No specific processing type found
                response = "Configuration error: No valid processing type found (jobs or cli)"

            return response

        except Exception as e:
            logger.exception(f"Error running AI agent: {e}")
            return f"Sorry, i'm having a little trouble with the LLM: usually it's ok, just send a message 'retry' to retry or go to the next step ('proceed' or click approve)."

    async def _get_ai_memory(self, entity: AgenticFlowEntity, config: Dict[str, Any],
                             memory: ChatMemory, technical_id: str) -> List[AIMessage]:
        """
        Get AI memory messages including input data from config.

        Args:
            entity: Agentic flow entity
            config: Configuration
            memory: Chat memory
            technical_id: Technical identifier

        Returns:
            List of AIMessage objects
        """
        memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])
        messages = []

        # Get existing memory messages
        for memory_tag in memory_tags:
            entity_messages: List[AIMessage] = memory.messages.get(memory_tag, [])
            for entity_message in entity_messages:
                message_content = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
                    entity_version=env_config.ENTITY_VERSION,
                    technical_id=entity_message.edge_message_id,
                    meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                )
                messages.append(message_content)

        # Handle input data from config
        input_data = config.get("input")
        if input_data:
            branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)

            # Handle local filesystem input
            if input_data.get("local_fs"):
                local_fs = input_data.get("local_fs")
                for file_name in local_fs:
                    try:
                        formatted_filename = file_name.format(**entity.workflow_cache)
                    except Exception as e:
                        formatted_filename = file_name
                        logger.exception(e)

                    path_contents = await self._read_local_path(
                        path_name=formatted_filename,
                        technical_id=branch_id,
                        branch_name_id=branch_id,
                        repository_name=self._get_repository_name(entity)
                    )
                    messages.append(AIMessage(role="user", content=f"Reference: {file_name}: \n {path_contents}"))

            # Handle cyoda edge message input
            elif input_data.get("cyoda_edge_message"):
                edge_messages = input_data.get("cyoda_edge_message")
                for edge_message in edge_messages:
                    message_content = await self.entity_service.get_item(
                        token=self.cyoda_auth_service,
                        entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                        entity_version=env_config.ENTITY_VERSION,
                        technical_id=entity.edge_messages_store.get(edge_message),
                        meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                    )
                    messages.append(AIMessage(role="user", content=f"Reference: {message_content}"))

        return messages

    async def _read_local_path(self, path_name: str, technical_id: str,
                               branch_name_id: str, repository_name: str) -> str:
        """
        Read local file or directory content.

        Args:
            path_name: File or directory name to read
            technical_id: Technical identifier
            branch_name_id: Branch name identifier
            repository_name: Repository name

        Returns:
            File content or directory listing with file contents as string
        """
        try:
            from common.utils.utils import get_project_file_name_path
            import os

            full_path = await get_project_file_name_path(
                technical_id=technical_id,
                git_branch_id=branch_name_id,
                file_name=path_name,
                repository_name=repository_name
            )

            # Check if path exists
            if not await self._path_exists(full_path):
                logger.warning(f"Path does not exist: {full_path}")
                return f"Path not found: {path_name}"

            # Check if it's a directory
            if await self._is_directory(full_path):
                return await self._read_local_directory(full_path, path_name)
            else:
                return await self._read_local_file(full_path, path_name)

        except Exception as e:
            logger.exception(f"Error during reading path {path_name}")
            return f"Error reading {path_name}: {str(e)}"

    async def _read_local_file(self, file_path: str, file_name: str) -> str:
        """
        Read local file content.

        Args:
            file_path: Full path to the file
            file_name: Original file name for reference

        Returns:
            File content as string
        """
        try:
            import aiofiles

            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                file_contents = await file.read()
            return file_contents

        except Exception as e:
            logger.exception(f"Error reading file {file_name}")
            return f"Error reading file {file_name}: {str(e)}"

    async def _read_local_directory(self, directory_path: str, directory_name: str) -> str:
        """
        Read local directory content recursively - list files and read each file's content from all subdirectories.

        Args:
            directory_path: Full path to the directory
            directory_name: Original directory name for reference

        Returns:
            Directory listing with file contents as formatted string
        """
        try:
            import os
            import asyncio

            files_content = []
            files_content.append(f"Directory: {directory_name}")
            files_content.append("=" * 50)

            # Get all files recursively
            all_files = await self._get_all_files_recursively(directory_path)

            if not all_files:
                files_content.append("Directory is empty or contains no readable files.")
                return "\n".join(files_content)

            files_content.append(f"Found {len(all_files)} files (including subdirectories):")
            files_content.append("")

            # Read each file's content
            for relative_file_path in sorted(all_files):
                full_file_path = os.path.join(directory_path, relative_file_path)

                try:
                    file_content = await self._read_local_file(full_file_path, relative_file_path)
                    files_content.append(f"--- File: {relative_file_path} ---")
                    files_content.append(file_content)
                    files_content.append("")
                except Exception as e:
                    logger.warning(f"Could not read file {relative_file_path}: {e}")
                    files_content.append(f"--- File: {relative_file_path} (Error reading) ---")
                    files_content.append(f"Error: {str(e)}")
                    files_content.append("")

            return "\n".join(files_content)

        except Exception as e:
            logger.exception(f"Error reading directory {directory_name}")
            return f"Error reading directory {directory_name}: {str(e)}"

    async def _path_exists(self, path: str) -> bool:
        """
        Check if a path exists asynchronously.

        Args:
            path: Path to check

        Returns:
            True if path exists, False otherwise
        """
        try:
            import os
            import asyncio
            return await asyncio.to_thread(os.path.exists, path)
        except Exception:
            return False

    async def _is_directory(self, path: str) -> bool:
        """
        Check if a path is a directory asynchronously.

        Args:
            path: Path to check

        Returns:
            True if path is a directory, False otherwise
        """
        try:
            import os
            import asyncio
            return await asyncio.to_thread(os.path.isdir, path)
        except Exception:
            return False

    async def _list_files_in_directory(self, directory_path: str) -> list:
        """
        List files in directory asynchronously (excluding subdirectories).

        Args:
            directory_path: Path to directory

        Returns:
            List of file names (not including subdirectories)
        """
        try:
            import os
            import asyncio

            def _list_files_sync():
                files = []
                for item_name in os.listdir(directory_path):
                    item_path = os.path.join(directory_path, item_name)
                    if os.path.isfile(item_path) and not item_name.startswith('.'):
                        files.append(item_name)
                return files

            return await asyncio.to_thread(_list_files_sync)
        except Exception as e:
            logger.debug(f"Error listing files in directory {directory_path}: {e}")
            return []

    async def _get_all_files_recursively(self, directory_path: str) -> list:
        """
        Get all files recursively from directory and all subdirectories.

        Args:
            directory_path: Path to directory

        Returns:
            List of relative file paths from the root directory
        """
        try:
            import os
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
            logger.debug(f"Error walking directory {directory_path}: {e}")
            return []

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

    async def _handle_batch_processing(self, config: Dict[str, Any]) -> str:
        """
        Handle batch processing configuration.
        
        Args:
            config: Batch processing configuration
            
        Returns:
            Batch processing result message
        """
        if batch_process_file is None:
            return "Batch processing not available (dependency issue)"

        try:
            input_file_path = config.get("input", {}).get("local_fs", [None])[0]
            output_file_path = config.get("output", {}).get("local_fs", [None])[0]

            if not input_file_path or not output_file_path:
                return "Invalid batch processing configuration: missing file paths"

            await batch_process_file(
                input_file_path=input_file_path,
                output_file_path=output_file_path
            )
            return f"Scheduled batch processing for {input_file_path}"

        except Exception as e:
            logger.exception(f"Error in batch processing: {e}")
            return f"Batch processing failed: {e}"

    async def process_ai_response(self, response: str, entity: AgenticFlowEntity,
                                  memory: ChatMemory, config: Dict[str, Any]) -> str:
        """
        Process AI agent response and handle any post-processing.
        
        Args:
            response: AI agent response
            entity: Agentic flow entity
            memory: Chat memory
            config: AI agent configuration
            
        Returns:
            Processed response
        """
        try:
            # Handle memory storage if needed
            memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])

            # Additional processing can be added here
            # For example: response validation, formatting, etc.

            return response

        except Exception as e:
            logger.exception(f"Error processing AI response: {e}")
            return response  # Return original response if processing fails

    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate AI agent configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not config:
            return False, "Configuration is empty"

        # Check for required fields based on type
        config_type = config.get("type")

        if config_type == "batch":
            input_config = config.get("input", {})
            output_config = config.get("output", {})

            if not input_config.get("local_fs"):
                return False, "Batch config missing input.local_fs"

            if not output_config.get("local_fs"):
                return False, "Batch config missing output.local_fs"

        elif config_type == "auggie":
            tasks = config.get("tasks", [])

            if not tasks:
                return False, "CLI config missing tasks array"

            for i, task in enumerate(tasks):
                if not task.get("instruction"):
                    return False, f"CLI task {i} missing instruction"

        # Add more validation rules as needed

        return True, ""

    async def handle_function_calling(self, function_name: str, parameters: Dict[str, Any],
                                      entity: AgenticFlowEntity, technical_id: str) -> Any:
        """
        Handle function calling from AI agent.
        
        Args:
            function_name: Name of the function to call
            parameters: Function parameters
            entity: Agentic flow entity
            technical_id: Technical identifier
            
        Returns:
            Function call result
        """
        try:
            if not self.method_registry.has_method(function_name):
                available_methods = self.method_registry.list_methods()
                return f"Function '{function_name}' not found. Available: {available_methods}"

            # Add entity and technical_id to parameters
            parameters.update({
                'entity': entity,
                'technical_id': technical_id
            })

            result = await self.method_registry.dispatch_method(method_name=function_name, **parameters)
            return result

        except Exception as e:
            logger.exception(f"Error in function calling '{function_name}': {e}")
            return f"Error calling function '{function_name}': {e}"

    def _check_and_update_iteration(self, config: Dict[str, Any], entity: AgenticFlowEntity) -> bool:
        """
        Check and update iteration count for the current transition.

        Args:
            config: Configuration containing max_iteration
            entity: Agentic flow entity

        Returns:
            True if max iteration exceeded, False otherwise
        """
        max_iteration = config.get("max_iteration")
        if max_iteration is None:
            return False

        transition = entity.current_transition
        iterations = entity.transitions_memory.current_iteration

        if transition not in iterations:
            iterations[transition] = 0
            entity.transitions_memory.max_iteration[transition] = max_iteration

        current_iteration = iterations[transition]
        if current_iteration > max_iteration:
            return True

        iterations[transition] = current_iteration + 1
        return False

    async def _append_messages(self, entity: AgenticFlowEntity, config: Dict[str, Any],
                               memory: ChatMemory, finished_flow: List[FlowEdgeMessage]) -> None:
        """
        Append configured messages to memory.

        Args:
            entity: Agentic flow entity
            config: Configuration containing messages
            memory: Chat memory
            finished_flow: Finished flow messages
        """
        memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])

        # Handle config messages
        if config.get("messages"):
            config_messages: List[AIMessage] = []
            for config_message in config.get("messages"):
                try:
                    config_message = await enrich_config_message(
                        entity_service=self.entity_service,
                        cyoda_auth_service=self.cyoda_auth_service,
                        entity=entity,
                        config_message=config_message
                    )
                except Exception as e:
                    logger.exception(e)
                    logger.error(config_message)

                edge_message_id = await self.entity_service.add_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
                    entity_version=env_config.ENTITY_VERSION,
                    entity=config_message,
                    meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                )
                config_messages.append(
                    AIMessage(edge_message_id=edge_message_id, last_modified=get_current_timestamp_num())
                )

            for memory_tag in memory_tags:
                memory.messages.setdefault(memory_tag, []).extend(config_messages)

        # Handle finished flow messages
        if finished_flow:
            latest_message = next(
                (msg for msg in reversed(finished_flow) if msg.type == "answer"),
                None
            )
            if latest_message and latest_message.type == "answer" and not latest_message.consumed:
                message_content: FlowEdgeMessage = await self.entity_service.get_item(
                    token=self.cyoda_auth_service,
                    entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                    entity_version=env_config.ENTITY_VERSION,
                    technical_id=latest_message.edge_message_id,
                    meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                )
                answer_content = message_content.message
                for memory_tag in memory_tags:
                    edge_message_id = await self.entity_service.add_item(
                        token=self.cyoda_auth_service,
                        entity_model=const.ModelName.AI_MEMORY_EDGE_MESSAGE.value,
                        entity_version=env_config.ENTITY_VERSION,
                        entity=AIMessage(role="user", content=answer_content),
                        meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
                    )
                    memory.messages.get(memory_tag).append(AIMessage(edge_message_id=edge_message_id))
                latest_message.consumed = True

    async def _run_auggie_background_task(self, config: Dict[str, Any], entity: AgenticFlowEntity,
                                          memory: ChatMemory, technical_id: str) -> None:
        """
        Run Auggie process in the background and update entity with 'complete_generation' transition when done.

        Args:
            config: Auggie agent configuration
            entity: Agentic flow entity
            memory: Chat memory
            technical_id: Technical identifier
        """
        try:
            logger.info(f"🚀 Starting CLI background task for entity {technical_id}")

            # Run the Auggie processor
            response = await self.auggie_processor.process_auggie_agent(config, entity, memory, technical_id)

            logger.info(f"✅ CLI background task completed for entity {technical_id}")
            logger.debug(f"CLI response: {response[:200]}{'...' if len(response) > 200 else ''}")

            # Update entity with 'complete_generation' transition
            await self._trigger_complete_generation_transition(technical_id=technical_id, entity=entity)

        except Exception as e:
            logger.error(f"❌ Error in CLI background task for entity {technical_id}: {e}")
            # The error is already logged, no need to re-raise since this is a background task

    async def _trigger_complete_generation_transition(self, technical_id: str, entity: AgenticFlowEntity) -> None:
        """
        Trigger the 'complete_generation' transition for the entity.

        Args:
            technical_id: Technical identifier of the entity
            entity: Agentic flow entity
        """
        try:
            logger.info(f"🔄 Triggering 'complete_generation' transition for entity {technical_id}")

            await self.entity_service.update_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.CHAT_ENTITY.value,
                entity_version=env_config.ENTITY_VERSION,
                technical_id=technical_id,
                entity=entity,
                meta={const.TransitionKey.UPDATE.value: "complete_generation"}
            )

            logger.info(f"✅ Successfully triggered 'complete_generation' transition for entity {technical_id}")

        except Exception as e:
            logger.error(f"❌ Failed to trigger 'complete_generation' transition for entity {technical_id}: {e}")
            # Don't re-raise since this is called from a background task
            # The CLI process has already completed successfully, so we just log the error

    async def _process_file_content_for_empty_messages(self, messages: List[AIMessage],
                                                       finished_flow: List[FlowEdgeMessage]) -> None:
        """
        Process file content for empty/minimal user messages by extracting first 100 and last 100 words
        from submitted files and modifying the user message in the messages list.

        Args:
            messages: List of AI messages to potentially modify
            finished_flow: Finished flow messages containing user answers and file attachments
        """
        try:
            # Find the latest user answer message
            latest_answer = next(
                (msg for msg in reversed(finished_flow) if msg.type == "answer"),
                None
            )

            if not latest_answer:
                return

            # Get the message content
            message_content: FlowEdgeMessage = await self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                entity_version=env_config.ENTITY_VERSION,
                technical_id=latest_answer.edge_message_id,
                meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )

            # Check if message is empty/minimal and has file attachments
            user_message = message_content.message
            file_blob_ids = message_content.file_blob_ids

            if (not user_message or len(str(user_message).strip()) < 10) and file_blob_ids:
                logger.info(f"Processing file content for empty/minimal user message with {len(file_blob_ids)} file(s)")

                # Extract content from the first file
                processed_message = await self._extract_file_content_for_message(file_blob_ids[0])

                if processed_message:
                    # Find and update the corresponding user message in the messages list
                    await self._update_user_message_with_file_content(messages, processed_message)

        except Exception as e:
            logger.exception(f"Error processing file content for empty messages: {e}")
            # Don't raise - this is optional processing, shouldn't break the flow

    async def _extract_file_content_for_message(self, file_blob_id: str) -> Optional[str]:
        """
        Extract file content from a blob and create a processed message with first 100 and last 100 words.
        """
        try:
            # Get the file blob
            file_blob: FlowEdgeMessage = await self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                entity_version=env_config.ENTITY_VERSION,
                technical_id=file_blob_id,
                meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )

            if file_blob.type != "file_blob":
                return None

            # Decode the base64 content and extract text
            import base64
            import io

            encoded_content = file_blob.message
            file_bytes = base64.b64decode(encoded_content)

            # Get filename from metadata
            metadata = file_blob.metadata or {}
            filename = metadata.get("filename", "unknown_file")

            # Create a file-like object for the file reader
            file_like = io.BytesIO(file_bytes)
            file_like.filename = filename

            # Use the existing file reader to extract text content
            from common.utils.file_reader import read_file_content
            file_content = read_file_content(file_like)

            # Convert to string if it's not already
            if not isinstance(file_content, str):
                file_content = str(file_content)

            # Apply word count processing (first 100 and last 100 words)
            words = file_content.split()
            if len(words) > 350:
                first_100 = " ".join(words[:100])
                last_100 = " ".join(words[-100:])
                processed_message = f"{first_100} [{const.USER_ATTACHED_FILE_MESSAGE}] {last_100}"
                logger.info(f"File content processed: {len(words)} words -> abridged message")
            else:
                processed_message = file_content
                logger.info(f"File content processed: {len(words)} words -> used as-is")

            return processed_message

        except Exception as e:
            logger.exception(f"Error extracting file content from blob {file_blob_id}: {e}")
            return None

    async def _update_user_message_with_file_content(self, messages: List[AIMessage], processed_message: str) -> None:
        """
        Update the last user message in the messages list with the processed file content.
        """
        try:
            # Find the last user message and update its content
            for message in reversed(messages):
                if message.role == "user":
                    # Update the message content with the processed file content
                    message.content = processed_message
                    logger.info("Updated user message with processed file content")
                    break

        except Exception as e:
            logger.exception(f"Error updating user message with file content: {e}")

    async def _extract_file_content_for_message(self, file_blob_id: str) -> Optional[str]:
        """
        Extract file content from a blob and create a processed message with first 100 and last 100 words.

        Args:
            file_blob_id: ID of the file blob to extract content from

        Returns:
            Processed message string or None if extraction fails
        """
        try:
            # Get the file blob
            file_blob: FlowEdgeMessage = await self.entity_service.get_item(
                token=self.cyoda_auth_service,
                entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                entity_version=env_config.ENTITY_VERSION,
                technical_id=file_blob_id,
                meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )

            if file_blob.type != "file_blob":
                logger.warning(f"Expected file_blob type, got {file_blob.type}")
                return None

            # Decode the base64 content
            import base64
            import io

            encoded_content = file_blob.message
            file_bytes = base64.b64decode(encoded_content)

            # Get filename from metadata
            metadata = file_blob.metadata or {}
            filename = metadata.get("filename", "unknown_file")

            # Create a file-like object for the file reader
            file_like = io.BytesIO(file_bytes)
            file_like.filename = filename

            # Use the existing file reader to extract text content
            from common.utils.file_reader import read_file_content
            file_content = read_file_content(file_like)

            # Convert to string if it's not already
            if not isinstance(file_content, str):
                file_content = str(file_content)

            # Apply word count processing (first 100 and last 100 words)
            words = file_content.split()
            if len(words) > 350:
                first_100 = " ".join(words[:100])
                last_100 = " ".join(words[-100:])
                processed_message = f"{first_100} [{const.USER_ATTACHED_FILE_MESSAGE}] {last_100}"
                logger.info(f"File content processed: {len(words)} words -> abridged message")
            else:
                processed_message = file_content
                logger.info(f"File content processed: {len(words)} words -> used as-is")

            return processed_message

        except Exception as e:
            logger.exception(f"Error extracting file content from blob {file_blob_id}: {e}")
            return None
