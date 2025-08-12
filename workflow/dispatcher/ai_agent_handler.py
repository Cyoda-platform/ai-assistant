import logging
from typing import Dict, Any, List
import common.config.const as const
from common.config.config import config as env_config
from common.utils.chat_util_functions import enrich_config_message
from common.utils.utils import get_current_timestamp_num
from entity.model import AgenticFlowEntity, ChatMemory, ModelConfig, FlowEdgeMessage, AIMessage

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

    def __init__(self, ai_agent, method_registry, memory_manager, cls_instance, entity_service, cyoda_auth_service):
        """
        Initialize the AI agent handler.

        Args:
            ai_agent: AI agent instance
            method_registry: Method registry for function calling
            memory_manager: Memory manager for chat operations
            cls_instance: Class instance for AI agent function calling
            entity_service: Entity service for edge message handling
            cyoda_auth_service: Cyoda auth service
        """
        self.ai_agent = ai_agent
        self.method_registry = method_registry
        self.memory_manager = memory_manager
        self.cls_instance = cls_instance
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
    
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
            await self._append_messages(entity=entity, memory=memory, config=config, finished_flow=finished_flow)

            # Get memory messages including input data
            memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])
            messages = await self._get_ai_memory(entity=entity, config=config, memory=memory, technical_id=technical_id)

            # Extract model configuration
            model = ModelConfig.model_validate(config.get("model", {}))

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

            # Store the response in memory
            await self.memory_manager.store_ai_response(response=response, memory=memory, memory_tags=memory_tags)

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
