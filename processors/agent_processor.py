"""
Agent processor for executing AI agents within workflows.

This processor handles the execution of AI agents with configurable models,
tools, and prompts. It supports both JSON-defined agents and SDK-based agents.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_processor import BaseProcessor, ProcessorContext, ProcessorResult
from .loaders.agent_loader import AgentLoader
from .loaders.tool_loader import ToolLoader


class AgentProcessor(BaseProcessor):
    """
    Processor for executing AI agents.
    
    Supports:
    - JSON-defined agents with model configurations
    - Tool integration and execution
    - Prompt loading from Markdown files
    - Memory management and tagging
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the agent processor.
        
        Args:
            base_path: Base directory path for loading resources
        """
        super().__init__("AgentProcessor")
        self.base_path = Path(base_path)
        self.agent_loader = AgentLoader(base_path)
        self.tool_loader = ToolLoader(base_path)
    
    def supports(self, processor_name: str) -> bool:
        """
        Check if this processor supports the given processor name.

        Args:
            processor_name: Name to check (format: "AgentProcessor.agent_name_with_underscores")

        Returns:
            True if processor name starts with "AgentProcessor."
        """
        return processor_name.startswith("AgentProcessor.") and len(processor_name.split(".", 1)) == 2
    
    async def execute(self, context: ProcessorContext) -> ProcessorResult:
        """
        Execute an AI agent based on the processor configuration.
        
        Args:
            context: Execution context containing agent configuration
            
        Returns:
            ProcessorResult with agent execution outcome
        """
        if not self.validate_context(context):
            return self.create_error_result("Invalid context provided")
        
        try:
            # Extract agent name from processor name (AgentProcessor.agent_name)
            processor_parts = context.config.get("processor_name", "").split(".", 1)
            if len(processor_parts) != 2 or processor_parts[0] != "AgentProcessor":
                return self.create_error_result("Invalid agent processor name format")
            
            agent_name = processor_parts[1]
            
            # Load agent configuration
            agent_config = self.agent_loader.load_agent(agent_name)
            if not agent_config:
                return self.create_error_result(f"Agent '{agent_name}' not found")
            
            # Execute the agent
            result = self._execute_agent(agent_config, context)
            
            return self.create_success_result(
                data=result,
                memory_updates=self._extract_memory_updates(result, context)
            )
            
        except Exception as e:
            return self.create_error_result(f"Agent execution failed: {str(e)}")
    
    def _execute_agent(self, agent_config: Dict[str, Any], context: ProcessorContext) -> Dict[str, Any]:
        """
        Execute the agent with the given configuration.
        
        Args:
            agent_config: Agent configuration dictionary
            context: Execution context
            
        Returns:
            Agent execution result
        """
        # Prepare agent execution parameters
        execution_params = {
            "model": agent_config.get("model", {}),
            "messages": self._prepare_messages(agent_config.get("messages", []), context),
            "tools": self._prepare_tools(agent_config.get("tools", []), context),
            "memory_tags": context.memory_tags or [],
            "entity_data": context.entity_data
        }
        
        # Execute based on agent type
        agent_type = agent_config.get("type", "agent")
        
        if agent_type == "agent":
            return self._execute_json_agent(execution_params, context)
        elif agent_type == "sdk":
            return self._execute_sdk_agent(agent_config, execution_params, context)
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")
    
    def _execute_json_agent(self, params: Dict[str, Any], context: ProcessorContext) -> Dict[str, Any]:
        """
        Execute a JSON-defined agent.
        
        Args:
            params: Execution parameters
            context: Execution context
            
        Returns:
            Execution result
        """
        # This would integrate with your existing AI execution framework
        # For now, return a placeholder result
        return {
            "type": "json_agent_result",
            "model": params["model"],
            "messages_count": len(params["messages"]),
            "tools_count": len(params["tools"]),
            "status": "executed"
        }
    
    def _execute_sdk_agent(
        self, 
        agent_config: Dict[str, Any], 
        params: Dict[str, Any], 
        context: ProcessorContext
    ) -> Dict[str, Any]:
        """
        Execute an SDK-based agent.
        
        Args:
            agent_config: Agent configuration
            params: Execution parameters
            context: Execution context
            
        Returns:
            Execution result
        """
        # Load and execute SDK agent class
        sdk_module = agent_config.get("sdk_module")
        if not sdk_module:
            raise ValueError("SDK agent missing sdk_module configuration")
        
        # This would dynamically import and execute the SDK agent
        # For now, return a placeholder result
        return {
            "type": "sdk_agent_result",
            "module": sdk_module,
            "status": "executed"
        }
    
    def _prepare_messages(self, messages: List[Dict[str, Any]], context: ProcessorContext) -> List[Dict[str, Any]]:
        """
        Prepare messages by loading content from files and applying context.
        
        Args:
            messages: Message configurations
            context: Execution context
            
        Returns:
            Prepared messages with content loaded
        """
        prepared_messages = []
        
        for message in messages:
            prepared_message = message.copy()
            
            # Load content from file if specified
            if "content_from_file" in message:
                file_path = self.base_path / message["content_from_file"]
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Remove YAML frontmatter if present
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                content = parts[2].strip()
                        prepared_message["content"] = content
                else:
                    prepared_message["content"] = f"File not found: {message['content_from_file']}"
            
            # Apply context variables to content
            if "content" in prepared_message and context.entity_data:
                prepared_message["content"] = self._apply_context_variables(
                    prepared_message["content"], 
                    context.entity_data
                )
            
            prepared_messages.append(prepared_message)
        
        return prepared_messages
    
    def _prepare_tools(self, tools: List[Dict[str, Any]], context: ProcessorContext) -> List[Dict[str, Any]]:
        """
        Prepare tools by loading configurations and applying context.
        
        Args:
            tools: Tool configurations
            context: Execution context
            
        Returns:
            Prepared tools with configurations loaded
        """
        prepared_tools = []
        
        for tool in tools:
            if "name" in tool:
                # Load tool from tools directory
                tool_config = self.tool_loader.load_tool(tool["name"])
                if tool_config:
                    prepared_tools.append(tool_config)
            else:
                # Use inline tool configuration
                prepared_tools.append(tool)
        
        return prepared_tools
    
    def _apply_context_variables(self, content: str, entity_data: Dict[str, Any]) -> str:
        """
        Apply context variables to content string.
        
        Args:
            content: Content string with variables
            entity_data: Entity data for variable substitution
            
        Returns:
            Content with variables replaced
        """
        # Simple variable substitution - can be enhanced
        for key, value in entity_data.items():
            content = content.replace(f"{{{key}}}", str(value))
        
        return content
    
    def _extract_memory_updates(self, result: Dict[str, Any], context: ProcessorContext) -> Optional[Dict[str, Any]]:
        """
        Extract memory updates from agent execution result.
        
        Args:
            result: Agent execution result
            context: Execution context
            
        Returns:
            Memory updates if any
        """
        # Extract memory updates based on memory tags and result
        if context.memory_tags and result:
            return {
                "tags": context.memory_tags,
                "content": result,
                "workflow": context.workflow_name,
                "state": context.state_name
            }
        
        return None
