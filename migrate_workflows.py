#!/usr/bin/env python3
"""
Workflow Migration Script

This script migrates legacy Cyoda workflows to the new processor-based architecture.
It converts old workflow JSON files to the new schema format and creates the necessary
agent, tool, and message files.

Usage:
    python migrate_workflows.py <workflow_file> [--output-dir <dir>] [--dry-run]

Example:
    python migrate_workflows.py old_workflow.json --output-dir ./migrated
"""

import argparse
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowMigrator:
    """
    Migrates legacy Cyoda workflows to processor-based architecture.
    
    Handles:
    - Converting workflow JSON schema
    - Extracting inline agents to separate files
    - Creating tool definitions for functions
    - Converting conditions to criteria
    - Preserving all configuration fields
    """

    def __init__(self, output_dir: str = "."):
        """
        Initialize the workflow migrator.
        
        Args:
            output_dir: Directory to output migrated files
        """
        self.output_dir = Path(output_dir) / "workflow_configs"
        self.created_files = []

    def migrate_workflow(self, workflow_file: str) -> Dict[str, Any]:
        """
        Migrate a workflow file to the new architecture.
        
        Args:
            workflow_file: Path to the workflow JSON file
            
        Returns:
            Migration result with success status and created files
        """
        try:
            # Load workflow
            with open(workflow_file, 'r') as f:
                old_workflow = json.load(f)

            logger.info(f"Migrating workflow: {old_workflow.get('workflow_name', 'unknown')}")

            # Create output directories
            self._create_directories()

            # Storage for extracted components
            agents = {}
            tools = {}
            messages = {}

            # Convert workflow
            new_workflow = self._convert_workflow_schema(old_workflow, agents, tools, messages)

            # Save workflow
            workflow_name = old_workflow.get('workflow_name', 'migrated_workflow')
            workflow_path = self.output_dir / "workflows" / f"{workflow_name}.json"
            self._save_json(workflow_path, new_workflow)

            # Save extracted components
            self._save_agents(agents)
            self._save_tools(tools)
            self._save_messages(messages)

            return {
                "success": True,
                "workflow_name": workflow_name,
                "created_files": self.created_files,
                "agents_created": len(agents),
                "tools_created": len(tools),
                "messages_created": len(messages)
            }

        except Exception as e:
            logger.exception(f"Migration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "created_files": self.created_files
            }

    def _create_directories(self):
        """Create necessary output directories."""
        directories = ["workflows", "agents", "tools", "messages", "prompts"]
        for dir_name in directories:
            dir_path = self.output_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)

    def _convert_workflow_schema(self, old_workflow: Dict[str, Any],
                                 agents: Dict[str, Dict[str, Any]],
                                 tools: Dict[str, Dict[str, Any]],
                                 messages: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert workflow to new schema format.
        
        Args:
            old_workflow: Original workflow definition
            agents: Dictionary to store extracted agents
            tools: Dictionary to store extracted tools
            messages: Dictionary to store extracted messages
            
        Returns:
            Converted workflow in new schema format
        """
        workflow_name = old_workflow.get('workflow_name', 'migrated_workflow')

        # Create new workflow structure
        new_workflow = {
            "version": "1.0",
            "name": workflow_name,
            "desc": f"Migrated from {workflow_name}",
            "initialState": old_workflow.get('initial_state', 'none'),
            "active": False,
            "criterion": {
                "type": "simple",
                "jsonPath": "$.workflow_name",
                "operation": "EQUALS",
                "value": workflow_name
            },
            "states": {}
        }

        # Convert states
        old_states = old_workflow.get('states', {})
        for state_name, state_config in old_states.items():
            new_workflow["states"][state_name] = self._convert_state(
                state_name, state_config, workflow_name, agents, tools, messages
            )

        return new_workflow

    def _convert_state(self, state_name: str, state_config: Dict[str, Any],
                       workflow_name: str, agents: Dict[str, Dict[str, Any]],
                       tools: Dict[str, Dict[str, Any]],
                       messages: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert a single state to new format.
        
        Args:
            state_name: Name of the state
            state_config: State configuration
            workflow_name: Name of the workflow
            agents: Dictionary to store extracted agents
            tools: Dictionary to store extracted tools
            messages: Dictionary to store extracted messages
            
        Returns:
            Converted state configuration
        """
        new_state = {
            "transitions": []
        }

        # Convert transitions
        old_transitions = state_config.get('transitions', {})
        for transition_name, transition_config in old_transitions.items():
            new_transition = self._convert_transition(
                state_name, transition_name, transition_config,
                workflow_name, agents, tools, messages
            )
            new_state["transitions"].append(new_transition)
            retry_transition = self._create_retry_transition(state_name=state_name)
            # todo
            # new_state["transitions"].append(retry_transition)
            # todo
            fail_transition = self._create_fail_transition(state_name=state_name)
            # new_state["transitions"].append(fail_transition)

        return new_state

    def _convert_transition(self, state_name: str, transition_name: str,
                            transition_config: Dict[str, Any], workflow_name: str,
                            agents: Dict[str, Dict[str, Any]],
                            tools: Dict[str, Dict[str, Any]],
                            messages: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert a single transition to new format.
        
        Args:
            state_name: Name of the current state
            transition_name: Name of the transition
            transition_config: Transition configuration
            workflow_name: Name of the workflow
            agents: Dictionary to store extracted agents
            tools: Dictionary to store extracted tools
            messages: Dictionary to store extracted messages
            
        Returns:
            Converted transition configuration
        """
        new_transition = {
            "name": transition_name,
            "next": transition_config.get("next", ""),
            "manual": transition_config.get("manual", False)
        }

        # Convert actions to processors
        action = transition_config.get("action", {})
        if action:
            processors = self._convert_action_to_processors(
                action, state_name, transition_name, workflow_name, agents, tools, messages
            )
            if processors:
                new_transition["processors"] = processors

        # Convert conditions to criteria
        condition = transition_config.get("condition", {})
        if condition:
            criterion = self._convert_condition_to_criterion(condition, tools)
            if criterion:
                new_transition["criterion"] = criterion

        return new_transition

    def _convert_action_to_processors(self, action: Dict[str, Any], state_name: str,
                                      transition_name: str, workflow_name: str,
                                      agents: Dict[str, Dict[str, Any]],
                                      tools: Dict[str, Dict[str, Any]],
                                      messages: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert action configuration to processors.
        
        Args:
            action: Action configuration
            state_name: Current state name
            transition_name: Current transition name
            workflow_name: Workflow name
            agents: Dictionary to store extracted agents
            tools: Dictionary to store extracted tools
            messages: Dictionary to store extracted messages
            
        Returns:
            List of processor configurations
        """
        processors = []
        config = action.get("config", {})
        action_type = config.get("type", "")

        if action_type in ["prompt", "agent"]:
            # Create agent processor
            agent_name = f'{transition_name}_{uuid.uuid4().hex[:4]}'

            # Extract agent configuration
            agent_config = config.copy()

            agent_config["messages"] = self._process_messages(config.get("messages", []), transition_name, messages)

            # Add agent-level fields
            agent_fields = ["publish", "approve", "allow_anonymous_users", "tool_choice", "max_iteration"]
            for field in agent_fields:
                if field in config:
                    agent_config[field] = config[field]

            # Add tools if present
            if "tools" in config:
                agent_config["tools"] = self._process_tools(config["tools"], tools)
                # Extract tool definitions
                for tool in config["tools"]:
                    if tool.get("type") == "function" and "function" in tool:
                        func_def = tool["function"]
                        if "name" in func_def:
                            tools[func_def["name"]] = tool

            agents[agent_name] = agent_config

            # Create processor reference
            processor_config = {
                "name": f"AgentProcessor.{agent_name}",
                "executionMode": "ASYNC_NEW_TX",
                "config": {
                    "calculationNodesTags": "ai_assistant"
                }
            }

            processors.append(processor_config)

        elif action_type == "function":
            # Create function processor
            function_config = config.get("function", {})
            if function_config and "name" in function_config:
                function_name = function_config["name"]

                # Create tool definition
                tool_config = config
                tools[function_name] = tool_config

                # Create processor reference
                processor_config = {
                    "name": f"FunctionProcessor.{function_name}",
                    "executionMode": "ASYNC_NEW_TX",
                    "config": {
                        "calculationNodesTags": "ai_assistant"
                    }
                }

                # Add workflow-level fields
                workflow_fields = ["input", "output", "response_format"]
                for field in workflow_fields:
                    if field in config:
                        processor_config[field] = config[field]

                processors.append(processor_config)

        elif action_type in ["question", "notification"]:
            # Create message processor
            message_name = f'{transition_name}_{uuid.uuid4().hex[:4]}'

            # Extract message content
            message_content = config.get("notification", config.get("question", ""))
            messages[message_name] = {
                "type": action_type,
                "content": message_content,
                "approve": config.get("approve", False),
                "publish": config.get("publish", False)
            }

            # Create processor reference
            processor_config = {
                "name": f"MessageProcessor.{message_name}",
                "executionMode": "ASYNC_NEW_TX",
                "config": {
                    "calculationNodesTags": "ai_assistant"
                }
            }

            # Add workflow-level fields
            workflow_fields = ["input", "output", "response_format"]
            for field in workflow_fields:
                if field in config:
                    processor_config[field] = config[field]

            processors.append(processor_config)

        return processors

    def _convert_condition_to_criterion(self, condition: Dict[str, Any],
                                        tools: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Convert old condition format to new criterion format.

        Args:
            condition: Old condition configuration
            tools: Dictionary to store extracted tools

        Returns:
            Criterion configuration or None if conversion not possible
        """
        # Handle nested config structure: "condition": {"config": {"type": "function", "function": {...}}}
        if "config" in condition:
            config = condition["config"]
            config_type = config.get("type")

            if config_type == "function":
                function_config = config.get("function", {})
                if function_config and "name" in function_config:
                    function_name = function_config["name"]

                    # Create tool configuration for condition function
                    tool_config = {
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "description": function_config.get("description", f"Condition function: {function_name}"),
                            "parameters": function_config.get("parameters", {
                                "type": "object",
                                "properties": {},
                                "required": []
                            })
                        }
                    }
                    tools[function_name] = tool_config

                    return {
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "config": {
                                "calculationNodesTags": "ai_assistant"
                            }
                        }
                    }

        # Handle direct condition structure
        condition_type = condition.get("type")

        if condition_type == "function":
            # Handle function-based criteria
            function_config = condition.get("function", {})
            if function_config and "name" in function_config:
                function_name = function_config["name"]

                # Create tool configuration for condition function
                tool_config = {
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "description": function_config.get("description", f"Condition function: {function_name}"),
                        "parameters": function_config.get("parameters", {
                            "type": "object",
                            "properties": {},
                            "required": []
                        })
                    }
                }
                tools[function_name] = tool_config

                return {
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "config": {
                            "calculationNodesTags": "ai_assistant"
                        }
                    }
                }
            elif "name" in condition:
                # Handle simple name-based condition
                function_name = condition["name"]

                # Create tool configuration for simple condition function
                tool_config = {
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "description": f"Condition function: {function_name}",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
                tools[function_name] = tool_config

                return {
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "config": {
                            "calculationNodesTags": "ai_assistant"
                        }
                    }
                }

        elif condition_type == "group":
            # Handle group-based criteria
            return {
                "type": "group",
                "name": condition.get("name", "criterion_group"),
                "operator": condition.get("operator", "AND"),
                "parameters": condition.get("parameters", [])
            }

        # Handle legacy condition format without explicit type
        elif "name" in condition and not condition_type:
            function_name = condition["name"]

            # Create tool configuration for legacy condition function
            tool_config = {
                "type": "function",
                "function": {
                    "name": function_name,
                    "description": f"Legacy condition function: {function_name}",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            tools[function_name] = tool_config

            return {
                "type": "function",
                "function": {
                    "name": function_name,
                    "config": {
                        "calculationNodesTags": "ai_assistant"
                    }
                }
            }

        return None

    def _process_messages(self, messages: List[Dict[str, Any]], transition_name: str,
                          messages_dict: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process messages and extract content to separate files.

        Args:
            messages: List of message configurations
            transition_name: Name of the transition
            messages_dict: Dictionary to store extracted messages

        Returns:
            List of processed messages with file references
        """
        processed_messages = []

        for i, message in enumerate(messages):
            processed_message = message.copy()

            # If message has inline content, extract it to a file
            if "content" in message:
                content = message["content"]

                # Handle both string and list content
                if isinstance(content, list):
                    content = "\n".join(content)

                message_name = f'{transition_name}_{uuid.uuid4().hex[:4]}'
                # Create message file path using just transition name
                message_file_path = f"prompts/{message_name}/message_{i}.md"

                # Store message content for saving
                messages_dict[message_file_path] = {
                    "type": "prompt",
                    "content": content
                }

                # Replace inline content with file reference
                processed_message = {
                    "role": message.get("role", "user"),
                    "content_from_file": message_name
                }

            processed_messages.append(processed_message)

        return processed_messages

    def _process_tools(self, tools: List[Dict[str, Any]], tools_dict: Dict[str, Dict[str, Any]]) -> List[
        Dict[str, Any]]:
        """
        Process tools and convert to name references.

        Args:
            tools: List of tool configurations
            tools_dict: Dictionary to store extracted tools

        Returns:
            List of processed tools with just name references
        """
        processed_tools = []

        for tool in tools:
            if tool.get("type") == "function" and "function" in tool:
                func_def = tool["function"]
                if "name" in func_def:
                    # Add just the name reference
                    processed_tools.append({"name": func_def["name"]})
            elif "name" in tool:
                # Already in correct format
                processed_tools.append({"name": tool["name"]})

        return processed_tools

    def _save_agents(self, agents: Dict[str, Dict[str, Any]]):
        """Save extracted agent configurations."""
        for agent_name, agent_config in agents.items():
            agent_dir = self.output_dir / "agents" / agent_name
            agent_dir.mkdir(parents=True, exist_ok=True)

            agent_file = agent_dir / "agent.json"
            self._save_json(agent_file, agent_config)

    def _save_tools(self, tools: Dict[str, Dict[str, Any]]):
        """Save extracted tool configurations."""
        for tool_name, tool_config in tools.items():
            tool_file = self.output_dir / "tools" / tool_name / "tool.json"
            self._save_json(tool_file, tool_config)

    def _save_messages(self, messages: Dict[str, Dict[str, Any]]):
        """Save extracted message configurations."""
        for message_path, message_config in messages.items():
            # Handle different message path formats
            if '/' in message_path:
                # This is a prompt file path (e.g., "prompts/transition_name/message_0.md")
                path_parts = message_path.split('/')
                message_dir = self.output_dir
                for part in path_parts[:-1]:
                    message_dir = message_dir / part
                message_dir.mkdir(parents=True, exist_ok=True)

                # Save as markdown file (path already includes .md extension)
                message_file = message_dir / path_parts[-1]
            else:
                # This is a simple message name (e.g., "transition_name")
                message_dir = self.output_dir / "messages"
                message_dir.mkdir(parents=True, exist_ok=True)

                # Save as markdown file
                message_file = message_dir / message_path / "message.md"

                message_meta_file = message_dir / message_path / "meta.json"

                os.makedirs(os.path.dirname(message_meta_file), exist_ok=True)
                meta_content = {"type": message_config["type"],
                                "approve": message_config.get("approve", False),
                                "publish": message_config.get("publish", False)}
                with open(message_meta_file, 'w') as f:
                    f.write(json.dumps(meta_content, indent=2))
                self.created_files.append(str(message_meta_file))

            content = f"{message_config['content']}"
            os.makedirs(os.path.dirname(message_file), exist_ok=True)
            with open(message_file, 'w') as f:
                f.write(content)
            self.created_files.append(str(message_file))

    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Save JSON data to file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        self.created_files.append(str(file_path))
        logger.info(f"Created: {file_path}")

    def _create_retry_transition(self, state_name):
        return {
            "name": 'retry',
            "next": state_name,
            "manual": True
        }

    def _create_fail_transition(self, state_name):
        return {
            "name": f'fail_{state_name}',
            "next": f'locked_{state_name}',
            "manual": False,
            "criterion": {
                "type": "group",
                "operator": "AND",
                "conditions": [
                    {
                        "type": "simple",
                        "jsonPath": "$.failed",
                        "operation": "EQUALS",
                        "value": True
                    }
                ]
            }
        }


def main():
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(description="Migrate Cyoda workflows to new architecture")
    #workflow_file = "/home/kseniia/IdeaProjects/ai-assistant-2/common/workflow/config/agentic_flow_entity/chat_entity/build_general_application_java.json"
    #workflow_file = '/home/kseniia/IdeaProjects/ai-assistant-2/common/workflow/config/chat_business_entity/chat_business_entity.json'
    workflow_file = '/home/kseniia/IdeaProjects/ai-assistant-2/common/workflow/config/agentic_flow_entity/chat_entity/chat_entity.json'
    parser.add_argument("--output-dir", default=".", help="Output directory for migrated files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without creating files")

    args = parser.parse_args()

    migrator = WorkflowMigrator(args.output_dir)

    if args.dry_run:
        print("DRY RUN MODE - No files will be created")
        # TODO: Implement dry run mode
        return 0

    result = migrator.migrate_workflow(workflow_file)

    if result["success"]:
        print(f"✅ Migration successful!")
        print(f"   Workflow: {result['workflow_name']}")
        print(f"   Files created: {len(result['created_files'])}")
        print(f"   Agents: {result['agents_created']}")
        print(f"   Tools: {result['tools_created']}")
        print(f"   Messages: {result['messages_created']}")
        return 0
    else:
        print(f"❌ Migration failed: {result['error']}")
        return 1


if __name__ == "__main__":
    exit(main())
