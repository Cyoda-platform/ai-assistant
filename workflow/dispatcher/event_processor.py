import asyncio
import json
import logging
from typing import Dict, Any, Tuple, List

import common.config.const as const
from common.config.config import config as env_config
from common.utils.utils import get_current_timestamp_num, _post_process_response, _save_file, get_repository_name
from entity.chat.chat import AgenticFlowEntity
from entity.model import WorkflowEntity, FlowEdgeMessage

logger = logging.getLogger(__name__)


class EventProcessor:
    """
    Handles event processing logic for workflow dispatcher.
    Coordinates between different components to process workflow events.
    """
    
    def __init__(self, method_registry, ai_agent_handler, memory_manager,
                 file_handler, message_processor, user_service, entity_service, cyoda_auth_service,
                 config_builder):
        """
        Initialize the event processor.

        Args:
            method_registry: Method registry for function dispatch
            ai_agent_handler: AI agent handler
            memory_manager: Memory manager
            file_handler: File handler
            message_processor: Message processor
            user_service: User service
            entity_service: Entity service for edge message handling
            cyoda_auth_service: Cyoda auth service
        """
        self.method_registry = method_registry
        self.ai_agent_handler = ai_agent_handler
        self.memory_manager = memory_manager
        self.file_handler = file_handler
        self.message_processor = message_processor
        self.user_service = user_service
        self.entity_service = entity_service
        self.cyoda_auth_service = cyoda_auth_service
        self._write_output_lock = asyncio.Lock()
        self.config_builder = config_builder
    
    async def process_event(self, entity: WorkflowEntity, processor_name: str,
                           technical_id: str) -> Tuple[WorkflowEntity, str]:
        """
        Process a workflow event.
        
        Args:
            entity: Workflow entity
            action: Action configuration
            technical_id: Technical identifier
            
        Returns:
            Tuple of (updated_entity, response)
        """
        response = "returned empty response"
        
        try:
            # Get user account information
            entity.user_id = await self.user_service.get_entity_account(user_id=entity.user_id)

            # Extract action name from processor name
            action_name = processor_name.split(".")[1] if "Processor." in processor_name else processor_name

            # If no "Processor." prefix, execute direct method
            if "Processor." not in processor_name:
                response = await self._execute_direct_method(
                    method_name=action_name, entity=entity, technical_id=technical_id
                )
            else:
                # Build config for processor-based actions
                try:
                    # Ensure proper processor name format
                    if not processor_name.startswith(("AgentProcessor.", "FunctionProcessor.", "MessageProcessor.")):
                        processor_name = f"FunctionProcessor.{action_name}"

                    config = self.config_builder.build_config(processor_name)

                    # Route to appropriate handler based on entity type and config
                    if config and config.get("type") and isinstance(entity, AgenticFlowEntity):
                        entity = AgenticFlowEntity(**entity.model_dump())
                        entity, response = await self._handle_agentic_flow_event(
                            config=config, entity=entity, technical_id=technical_id
                        )
                    elif config and config.get("type") and isinstance(entity, WorkflowEntity):
                        response = await self._handle_workflow_entity_event(
                            config=config, entity=entity, technical_id=technical_id
                        )
                    else:
                        # Fallback to direct method execution if config doesn't match expected patterns
                        if self.method_registry.has_method(action_name):
                            response = await self._execute_direct_method(
                                method_name=action_name, entity=entity, technical_id=technical_id
                            )
                        else:
                            raise ValueError(f"Unknown processing step: {action_name}")

                except (FileNotFoundError, ValueError) as config_error:
                    logger.warning(f"Config build failed for {processor_name}: {config_error}. Trying direct method execution.")
                    # Fallback to direct method execution if config building fails
                    if self.method_registry.has_method(action_name):
                        response = await self._execute_direct_method(
                            method_name=action_name, entity=entity, technical_id=technical_id
                        )
                    else:
                        raise ValueError(f"Unknown processing step: {action_name}") from config_error

        except Exception as e:
            entity.failed = True
            entity.last_modified = get_current_timestamp_num()
            entity.error = f"Error: {e}"
            logger.exception(f"Exception occurred while processing event: {e}")
        
        logger.info(f"{processor_name}: {response}")
        entity.last_modified = get_current_timestamp_num()
        return entity, response
    
    async def _handle_agentic_flow_event(self, config: Dict[str, Any],
                                        entity: AgenticFlowEntity,
                                        technical_id: str) -> Tuple[AgenticFlowEntity, str]:
        """
        Handle events for agentic flow entities.

        Args:
            config: Event configuration
            entity: Agentic flow entity
            technical_id: Technical identifier

        Returns:
            Tuple of (updated_entity, response)
        """
        response = None
        config_type = config.get("type")
        finished_flow = entity.chat_flow.finished_flow
        child_entities_size_before = len(entity.child_entities)

        try:
            # Handle different config types
            if config_type in ("notification", "question"):
                response = await self._handle_notification_or_question(config=config, entity=entity)
            elif config_type == "function":
                response = await self._handle_function_call(config=config, entity=entity, technical_id=technical_id)
            elif config_type in ("prompt", "agent", "batch"):
                response = await self._handle_ai_agent_call(config=config, entity=entity, technical_id=technical_id)
            else:
                logger.warning(f"Unknown config type: {config_type}")
                response = f"Unknown config type: {config_type}"

            # Calculate new entities created during processing
            new_entities = entity.child_entities[child_entities_size_before:] if child_entities_size_before < len(
                entity.child_entities) else []

            # Finalize response with proper workflow management
            await self._finalize_response(
                technical_id=technical_id,
                config=config,
                entity=entity,
                finished_flow=finished_flow,
                new_entities=new_entities,
                response=response
            )

        except Exception as e:
            logger.exception(f"Error handling agentic flow event: {e}")
            response = f"Error: {e}"

        return entity, response or "No response generated"
    
    async def _handle_workflow_entity_event(self, config: Dict[str, Any], 
                                           entity: WorkflowEntity, 
                                           technical_id: str) -> str:
        """
        Handle events for workflow entities.
        
        Args:
            config: Event configuration
            entity: Workflow entity
            technical_id: Technical identifier
            
        Returns:
            Response string
        """
        try:
            if config["type"] == "function":
                params = config["function"].get("parameters", {})
                return await self.method_registry.dispatch_method(
                    config["function"]["name"],
                    technical_id=technical_id,
                    entity=entity,
                    **params
                )
            else:
                return f"Unsupported config type for WorkflowEntity: {config['type']}"
                
        except Exception as e:
            logger.exception(f"Error handling workflow entity event: {e}")
            return f"Error: {e}"
    
    async def _execute_direct_method(self, method_name: str, entity: WorkflowEntity, 
                                    technical_id: str) -> str:
        """
        Execute a direct method call.
        
        Args:
            method_name: Name of the method to execute
            entity: Workflow entity
            technical_id: Technical identifier
            
        Returns:
            Method execution result
        """
        try:
            return await self.method_registry.dispatch_method(
                method_name=method_name,
                technical_id=technical_id,
                entity=entity
            )
        except Exception as e:
            logger.exception(f"Error executing direct method '{method_name}': {e}")
            entity.failed = True
            entity.error = f"Error executing method '{method_name}': {e}"
            raise
    
    async def _handle_notification_or_question(self, config: Dict[str, Any],
                                              entity: AgenticFlowEntity) -> str:
        """
        Handle notification or question type configs.

        Args:
            config: Configuration
            entity: Agentic flow entity

        Returns:
            Formatted message
        """
        config_type = config.get("type")
        message = config.get(config_type, "")

        # Format message with entity cache
        formatted_message = self._format_message(message=message, cache=entity.workflow_cache)

        # Update config with formatted message (important for downstream processing)
        config[config_type] = formatted_message

        # Store in memory if needed
        memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])
        if memory_tags:
            await self.memory_manager.append_to_ai_memory(
                entity=entity, content=formatted_message, memory_tags=memory_tags
            )

        return formatted_message
    
    async def _handle_function_call(self, config: Dict[str, Any], 
                                   entity: AgenticFlowEntity, 
                                   technical_id: str) -> str:
        """
        Handle function call type configs.
        
        Args:
            config: Configuration
            entity: Agentic flow entity
            technical_id: Technical identifier
            
        Returns:
            Function call result
        """
        function_config = config.get("function", {})
        function_name = function_config.get("name")
        parameters = function_config.get("parameters", {})
        
        if not function_name:
            return "Error: Function name not specified"
        
        response = await self.ai_agent_handler.handle_function_calling(
            function_name=function_name, parameters=parameters, entity=entity, technical_id=technical_id
        )
        
        # Store response in memory if needed
        if response and isinstance(response, str):
            memory_tags = config.get("memory_tags", [env_config.GENERAL_MEMORY_TAG])
            if memory_tags:
                await self.memory_manager.append_to_ai_memory(
                    entity=entity, content=response, memory_tags=memory_tags
                )
        
        return str(response)
    
    async def _handle_ai_agent_call(self, config: Dict[str, Any], 
                                   entity: AgenticFlowEntity, 
                                   technical_id: str) -> str:
        """
        Handle AI agent call type configs.
        
        Args:
            config: Configuration
            entity: Agentic flow entity
            technical_id: Technical identifier
            
        Returns:
            AI agent response
        """
        # Get chat memory
        chat_memory = await self.memory_manager.get_chat_memory(memory_id=entity.memory_id)

        # Run AI agent
        response = await self.ai_agent_handler.run_ai_agent(
            config=config, entity=entity, memory=chat_memory, technical_id=technical_id
        )

        # Update chat memory
        await self.memory_manager.update_chat_memory(memory_id=entity.memory_id, chat_memory=chat_memory)
        
        return response
    
    def _format_message(self, message: str, cache: Dict[str, Any]) -> str:
        """
        Format message with cache values.

        Args:
            message: Message template
            cache: Cache values for formatting

        Returns:
            Formatted message
        """
        try:
            return message.format(**cache)
        except Exception as e:
            logger.exception(f"Error formatting message: {e}")
            return message

    async def _finalize_response(self, technical_id: str, entity: AgenticFlowEntity,
                                config: Dict[str, Any], finished_flow: List[FlowEdgeMessage],
                                response: str, new_entities: List[Any]) -> None:
        """
        Finalize response by creating edge messages and handling workflow state.

        Args:
            technical_id: Technical identifier
            entity: Agentic flow entity
            config: Configuration
            finished_flow: Finished flow messages
            response: Response content
            new_entities: New entities created during processing
        """
        # Create initial edge message
        message = FlowEdgeMessage(
            type=config.get("type"),
            approve=config.get('approve'),
            publish=config.get('publish'),
            message=config.get(config.get("type")),
            last_modified=get_current_timestamp_num()
        )
        await self.add_edge_message(message=message, flow=finished_flow, user_id=entity.user_id)
        config_type = config["type"]

        if config_type in ("function", "prompt", "agent"):

            if response and response != "None":
                if isinstance(response, str) and response.strip().startswith('{\"type\": \"ui_function\"'):
                    response = json.loads(response)
                    notification = FlowEdgeMessage(
                        publish=config.get("publish", False),
                        message=_post_process_response(response=f"{response}", config=config),
                        approve=config.get("approve", False),
                        type=const.UI_FUNCTION_PREFIX
                    )
                else:
                    notification = FlowEdgeMessage(
                        publish=config.get("publish", False),
                        message=_post_process_response(response=f"{response}", config=config),
                        approve=config.get("approve", False),
                        type="question"
                    )
                await self.add_edge_message(message=notification,
                                            flow=finished_flow,
                                            user_id=entity.user_id)

            # Handle output writing with lock protection
            async with self._write_output_lock:
                await self._write_to_output(entity=entity,
                                            config=config,
                                            response=response,
                                            technical_id=technical_id)

        # Handle new entities
        if new_entities:
            message = FlowEdgeMessage(type="child_entities",
                                      message=new_entities,
                                      last_modified=get_current_timestamp_num())
            await self.add_edge_message(message=message, flow=finished_flow,
                                        user_id=entity.user_id)

    async def add_edge_message(self, message: FlowEdgeMessage, flow: List[FlowEdgeMessage], user_id: str) -> FlowEdgeMessage:
        """
        Add an edge message to the flow.

        Args:
            message: FlowEdgeMessage to add
            flow: List of flow edge messages
            user_id: User ID

        Returns:
            Created FlowEdgeMessage with edge_message_id
        """
        edge_message_id = await self.entity_service.add_item(
            token=self.cyoda_auth_service,
            entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
            entity_version=env_config.ENTITY_VERSION,
            entity=message,
            meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
        )

        flow_edge_message = FlowEdgeMessage(
            type=message.type,
            publish=message.publish,
            edge_message_id=edge_message_id,
            last_modified=message.last_modified,
            user_id=user_id
        )
        flow.append(flow_edge_message)
        return flow_edge_message

    async def _write_to_output(self, entity: AgenticFlowEntity, config: Dict[str, Any],
                              response: str, technical_id: str) -> None:
        """
        Write response to output if configured.

        Args:
            entity: Agentic flow entity
            config: Configuration
            response: Response content
            technical_id: Technical identifier
        """
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
                    await self._save_file(_data=response,
                                         item=formatted_filename,
                                         git_branch_id=branch_id,
                                         repository_name=self._get_repository_name(entity))
            if config.get("output").get("workflow_cache"):
                cache_keys = config.get("output").get("workflow_cache")
                for cache_key in cache_keys:
                    entity.workflow_cache[cache_key] = response
            if config.get("output").get("cyoda_edge_message"):
                edge_messages = config.get("output").get("cyoda_edge_message")
                for edge_message in edge_messages:
                    edge_message_id = await self.entity_service.add_item(token=self.cyoda_auth_service,
                                                                         entity_model=const.ModelName.EDGE_MESSAGE_STORE.value,
                                                                         entity_version=env_config.ENTITY_VERSION,
                                                                         entity=response,
                                                                         meta={
                                                                             "type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE})
                    entity.edge_messages_store[edge_message] = edge_message_id

    async def _save_file(self, _data: str, item: str, git_branch_id: str, repository_name: str) -> None:
        """
        Save file using the original _save_file utility.

        Args:
            _data: File content
            item: File path
            git_branch_id: Git branch ID
            repository_name: Repository name
        """
        await _save_file(_data=_data, item=item, git_branch_id=git_branch_id, repository_name=repository_name)

    def _get_repository_name(self, entity: AgenticFlowEntity) -> str:
        """
        Get repository name using the original get_repository_name utility.

        Args:
            entity: Agentic flow entity

        Returns:
            Repository name
        """
        return get_repository_name(entity)
