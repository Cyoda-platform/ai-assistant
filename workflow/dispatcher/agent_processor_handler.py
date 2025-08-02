"""
Agent Processor Handler for the new processor-based workflow architecture.

This handler bridges between the new AgentProcessor architecture and the existing
AI agent functionality, converting agent configurations to the format expected
by the existing AI agent infrastructure.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from entity.model import AgenticFlowEntity, ChatMemory, ModelConfig, AIMessage, FlowEdgeMessage
from processors.loaders.agent_loader import AgentLoader
from processors.loaders.tool_loader import ToolLoader
from processors.base_processor import ProcessorContext, ProcessorResult
from .ai_agent_handler import AIAgentHandler
from common.utils.utils import get_current_timestamp_num, _post_process_response
import common.config.const as const
import json

logger = logging.getLogger(__name__)


class AgentProcessorHandler:
    """
    Handler for AgentProcessor execution within the workflow dispatcher.

    This class bridges the new processor architecture with the existing AI agent
    infrastructure by:
    1. Loading agent configurations from the agent_configs/ directory
    2. Converting them to the format expected by AIAgentHandler
    3. Managing the execution flow and result processing
    """
    
    def __init__(self, ai_agent_handler: AIAgentHandler, entity_service=None, base_path: str = "."):
        """
        Initialize the agent processor handler.

        Args:
            ai_agent_handler: Existing AI agent handler instance
            entity_service: Entity service for edge message handling
            base_path: Base path for loading agent configurations
        """
        self.ai_agent_handler = ai_agent_handler
        self.entity_service = entity_service or ai_agent_handler.entity_service
        self.base_path = Path(base_path)
        self.agent_loader = AgentLoader(base_path)
        self.tool_loader = ToolLoader(base_path)
    
    async def execute_agent_processor(self, agent_name: str, context: ProcessorContext,
                                    entity: AgenticFlowEntity) -> ProcessorResult:
        """
        Execute an agent processor with full workflow management.

        Args:
            agent_name: Name of the agent to execute
            context: Processor execution context
            entity: Agentic flow entity

        Returns:
            ProcessorResult with execution outcome
        """
        try:
            # Load agent configuration
            agent_config = await self.agent_loader.load_agent(agent_name)
            if not agent_config:
                return ProcessorResult(
                    success=False,
                    error_message=f"Agent '{agent_name}' not found"
                )

            # Track child entities before processing
            finished_flow = entity.chat_flow.finished_flow
            child_entities_size_before = len(entity.child_entities)

            # Convert agent config to legacy format
            legacy_config = await self._convert_agent_config_to_legacy(agent_config, context, entity)

            # Get chat memory
            memory = await self.ai_agent_handler.memory_manager.get_chat_memory(
                memory_id=entity.memory_id
            )

            # Execute using existing AI agent handler
            response = await self.ai_agent_handler.run_ai_agent(
                config=legacy_config,
                entity=entity,
                memory=memory,
                technical_id=context.entity_id
            )

            # Update chat memory
            await self.ai_agent_handler.memory_manager.update_chat_memory(
                memory_id=entity.memory_id,
                chat_memory=memory
            )

            # Calculate new entities created during processing
            new_entities = entity.child_entities[child_entities_size_before:] if child_entities_size_before < len(
                entity.child_entities) else []

            # Finalize response with workflow management
            await self._finalize_agent_response(
                technical_id=context.entity_id,
                agent_config=agent_config,
                legacy_config=legacy_config,
                entity=entity,
                finished_flow=finished_flow,
                new_entities=new_entities,
                response=response
            )

            # Create processor result
            result_data = {
                "response": response,
                "agent_name": agent_name,
                "execution_type": "agent",
                "new_entities_count": len(new_entities)
            }

            # Extract memory updates if needed
            memory_updates = None
            if legacy_config.get("memory_tags"):
                memory_updates = {
                    "tags": legacy_config["memory_tags"],
                    "content": response,
                    "workflow": context.workflow_name,
                    "state": context.state_name
                }

            return ProcessorResult(
                success=True,
                data=result_data,
                memory_updates=memory_updates
            )

        except Exception as e:
            logger.exception(f"Error executing agent processor '{agent_name}': {e}")
            return ProcessorResult(
                success=False,
                error_message=str(e)
            )
    
    async def _convert_agent_config_to_legacy(self, agent_config: Dict[str, Any], 
                                            context: ProcessorContext,
                                            entity: AgenticFlowEntity) -> Dict[str, Any]:
        """
        Convert new agent configuration to legacy format expected by AIAgentHandler.
        
        Args:
            agent_config: New agent configuration
            context: Processor context
            entity: Agentic flow entity
            
        Returns:
            Legacy configuration dictionary
        """
        legacy_config = {
            "type": "agent",  # Default type for AI agent processing
            "publish": agent_config.get("publish", False),  # Use agent config value
            "approve": agent_config.get("approve", False),  # Use agent config value
            "model": agent_config.get("model", {}),
            "memory_tags": agent_config.get("memory_tags", []),
            "messages": [],
            "tools": []
        }

        # Add agent-level configuration fields
        for field in ["allow_anonymous_users", "tool_choice", "max_iteration"]:
            if field in agent_config:
                legacy_config[field] = agent_config[field]
        
        # Convert messages
        if "messages" in agent_config:
            legacy_config["messages"] = await self._convert_messages(
                agent_config["messages"], context, entity
            )
        
        # Convert tools
        if "tools" in agent_config:
            legacy_config["tools"] = await self._convert_tools(agent_config["tools"])
        
        # Handle other agent config properties
        for key in ["tool_choice", "response_format", "max_iteration"]:
            if key in agent_config:
                legacy_config[key] = agent_config[key]
        
        return legacy_config
    
    async def _convert_messages(self, messages: List[Dict[str, Any]], 
                              context: ProcessorContext,
                              entity: AgenticFlowEntity) -> List[Dict[str, Any]]:
        """
        Convert agent messages to legacy format.
        
        Args:
            messages: Agent messages configuration
            context: Processor context
            entity: Agentic flow entity
            
        Returns:
            Legacy messages format
        """
        converted_messages = []
        
        for message in messages:
            converted_message = message.copy()
            
            # Handle content_from_file
            if "content_from_file" in message:
                content = await self._load_message_content(message["content_from_file"])
                if content:
                    # Apply context variable substitution
                    content = self._apply_context_variables(content, context.entity_data or {})
                    converted_message["content"] = content
                    # Remove the file reference
                    del converted_message["content_from_file"]
            
            # Apply context variables to existing content
            elif "content" in converted_message:
                converted_message["content"] = self._apply_context_variables(
                    converted_message["content"], 
                    context.entity_data or {}
                )
            
            converted_messages.append(converted_message)
        
        return converted_messages
    
    async def _load_message_content(self, file_path: str) -> Optional[str]:
        """
        Load message content from file.
        
        Args:
            file_path: Path to the message file
            
        Returns:
            Message content or None if not found
        """
        try:
            full_path = self.base_path / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove YAML frontmatter if present
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        content = parts[2].strip()
                
                return content
            else:
                logger.warning(f"Message file not found: {file_path}")
                return None
                
        except Exception as e:
            logger.exception(f"Error loading message content from {file_path}: {e}")
            return None
    
    async def _convert_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert agent tools to legacy format.
        
        Args:
            tools: Agent tools configuration
            
        Returns:
            Legacy tools format
        """
        converted_tools = []
        
        for tool in tools:
            if "name" in tool:
                # Load tool configuration
                tool_config = await self.tool_loader.load_tool(tool["name"])
                if tool_config:
                    # Convert to legacy format expected by AI agent
                    if tool_config.get("type") == "function":
                        converted_tools.append({
                            "type": "function",
                            "function": tool_config["function"]
                        })
                    else:
                        # Use tool config as-is for other types
                        converted_tools.append(tool_config)
                else:
                    logger.warning(f"Tool '{tool['name']}' not found")
            else:
                # Use inline tool configuration
                converted_tools.append(tool)
        
        return converted_tools
    
    def _apply_context_variables(self, content: str, entity_data) -> str:
        """
        Apply context variables to content string.

        Args:
            content: Content string with variables
            entity_data: Entity object or dictionary for variable substitution

        Returns:
            Content with variables replaced
        """
        try:
            # Handle both entity objects and dictionaries
            if hasattr(entity_data, 'model_dump'):
                # Entity object with model_dump method (Pydantic model)
                data_dict = entity_data.model_dump()
            elif hasattr(entity_data, '__dict__'):
                # Entity object with __dict__
                data_dict = entity_data.__dict__
            elif isinstance(entity_data, dict):
                # Already a dictionary
                data_dict = entity_data
            else:
                # Fallback: try to convert to dict
                data_dict = {}

            # Simple variable substitution
            for key, value in data_dict.items():
                if isinstance(value, (str, int, float, bool)):
                    content = content.replace(f"{{{key}}}", str(value))

            return content
        except Exception as e:
            logger.exception(f"Error applying context variables: {e}")
            return content
    
    def validate_agent_config(self, agent_name: str) -> Tuple[bool, str]:
        """
        Validate an agent configuration.
        
        Args:
            agent_name: Name of the agent to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            agent_config = self.agent_loader.load_agent(agent_name)
            if not agent_config:
                return False, f"Agent '{agent_name}' not found"
            
            # Validate agent configuration structure
            validation_result = self.agent_loader.validate_agent(agent_name)
            return validation_result["valid"], ", ".join(validation_result["errors"])
            
        except Exception as e:
            logger.exception(f"Error validating agent config '{agent_name}': {e}")
            return False, f"Validation error: {e}"

    async def _finalize_agent_response(self, technical_id: str, agent_config: Dict[str, Any],
                                     legacy_config: Dict[str, Any], entity: AgenticFlowEntity,
                                     finished_flow: List[FlowEdgeMessage], response: str,
                                     new_entities: List[Any]) -> None:
        """
        Finalize agent response by creating edge messages and handling workflow state.

        Args:
            technical_id: Technical identifier
            agent_config: Original agent configuration
            legacy_config: Converted legacy configuration
            entity: Agentic flow entity
            finished_flow: Finished flow messages
            response: Agent response content
            new_entities: New entities created during processing
        """
        try:
            # Create initial edge message for agent execution
            message = FlowEdgeMessage(
                type="agent",
                approve=legacy_config.get('approve', False),
                publish=legacy_config.get('publish', False),
                message=f"Agent {agent_config.get('type', 'agent')} executed",
                last_modified=get_current_timestamp_num()
            )
            await self._add_edge_message(message=message, flow=finished_flow, user_id=entity.user_id)

            # Handle agent response
            if response and response != "None":
                if isinstance(response, str) and response.strip().startswith('{\"type\": \"ui_function\"'):
                    response_data = json.loads(response)
                    notification = FlowEdgeMessage(
                        publish=legacy_config.get("publish", False),
                        message=_post_process_response(response=f"{response_data}", config=legacy_config),
                        approve=legacy_config.get("approve", False),
                        type=const.UI_FUNCTION_PREFIX
                    )
                else:
                    notification = FlowEdgeMessage(
                        publish=legacy_config.get("publish", False),
                        message=_post_process_response(response=f"{response}", config=legacy_config),
                        approve=legacy_config.get("approve", False),
                        type="question"
                    )
                await self._add_edge_message(message=notification, flow=finished_flow, user_id=entity.user_id)

                # Handle output writing
                await self._write_agent_output(
                    entity=entity,
                    agent_config=agent_config,
                    legacy_config=legacy_config,
                    response=response,
                    technical_id=technical_id
                )

            # Handle new entities
            if new_entities:
                message = FlowEdgeMessage(
                    type="child_entities",
                    message=new_entities,
                    last_modified=get_current_timestamp_num()
                )
                await self._add_edge_message(message=message, flow=finished_flow, user_id=entity.user_id)

        except Exception as e:
            logger.exception(f"Error finalizing agent response: {e}")

    async def _add_edge_message(self, message: FlowEdgeMessage, flow: List[FlowEdgeMessage], user_id: str) -> FlowEdgeMessage:
        """
        Add an edge message to the flow.

        Args:
            message: FlowEdgeMessage to add
            flow: List of flow edge messages
            user_id: User ID

        Returns:
            Added FlowEdgeMessage with edge_message_id
        """
        try:
            from common.config.config import config as env_config

            edge_message_id = await self.entity_service.add_item(
                token=self.ai_agent_handler.cyoda_auth_service,
                entity_model=const.ModelName.FLOW_EDGE_MESSAGE.value,
                entity_version=env_config.ENTITY_VERSION,
                entity=message,
                meta={"type": env_config.CYODA_ENTITY_TYPE_EDGE_MESSAGE}
            )
            message.edge_message_id = edge_message_id
            flow.append(message)
            return message

        except Exception as e:
            logger.exception(f"Error adding edge message: {e}")
            return message

    async def _write_agent_output(self, entity: AgenticFlowEntity, agent_config: Dict[str, Any],
                                legacy_config: Dict[str, Any], response: str, technical_id: str) -> None:
        """
        Write agent output to configured destinations.

        Args:
            entity: Agentic flow entity
            agent_config: Original agent configuration
            legacy_config: Converted legacy configuration
            response: Agent response
            technical_id: Technical identifier
        """
        try:
            # Check if output configuration exists
            output_config = legacy_config.get("output")
            if not output_config:
                return

            # Handle local filesystem output
            if output_config.get("local_fs"):
                for file_name in output_config["local_fs"]:
                    try:
                        formatted_filename = file_name.format(**entity.workflow_cache)
                    except Exception as e:
                        formatted_filename = file_name
                        logger.exception(f"Error formatting filename {file_name}: {e}")

                    await self._write_to_local_file(
                        file_name=formatted_filename,
                        content=response,
                        technical_id=technical_id,
                        entity=entity
                    )

            # Handle other output types as needed
            # (cyoda_edge_message, etc.)

        except Exception as e:
            logger.exception(f"Error writing agent output: {e}")

    async def _write_to_local_file(self, file_name: str, content: str,
                                 technical_id: str, entity: AgenticFlowEntity) -> None:
        """
        Write content to local file.

        Args:
            file_name: File name to write to
            content: Content to write
            technical_id: Technical identifier
            entity: Agentic flow entity
        """
        try:
            from common.utils.utils import get_project_file_name_path, _save_file

            branch_id = entity.workflow_cache.get(const.GIT_BRANCH_PARAM, technical_id)
            repository_name = self._get_repository_name(entity)

            file_path = await get_project_file_name_path(
                technical_id=technical_id,
                git_branch_id=branch_id,
                file_name=file_name,
                repository_name=repository_name
            )

            await _save_file(file_path=file_path, file_contents=content)
            logger.info(f"Agent output written to: {file_path}")

        except Exception as e:
            logger.exception(f"Error writing to local file {file_name}: {e}")

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
