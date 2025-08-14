#!/usr/bin/env python3
"""
Convert Python code configurations back to JSON configs

This script converts the generated Python code in workflow_config_code/
back to JSON configuration files in workflow_config_generated/
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
import importlib.util
import shutil


class CodeToConfigConverter:
    """Converts Python code configurations back to JSON configs"""
    
    def __init__(self, source_dir: str = "workflow_config_code", target_dir: str = "workflow_configs"):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
        # Add source directory to Python path for imports
        sys.path.insert(0, str(self.source_dir.absolute()))
    
    def convert_all(self):
        """Convert all Python configurations back to JSON"""
        print("🔄 CONVERTING CODE TO JSON CONFIGS")
        print("=" * 40)
        
        # Create target directory
        self.target_dir.mkdir(exist_ok=True)
        
        # Convert each type
        self.convert_agents()
        self.convert_messages()
        self.convert_tools()
        self.convert_prompts()
        self.convert_workflows()
        
        print(f"\n✅ Conversion complete! Generated configs in: {self.target_dir}")
    
    def convert_agents(self):
        """Convert agent Python code back to JSON configs"""
        print("\n📋 Converting agents...")
        
        agents_source_dir = self.source_dir / "agents"
        agents_target_dir = self.target_dir / "agents"
        agents_target_dir.mkdir(exist_ok=True)
        
        if not agents_source_dir.exists():
            return
            
        for agent_dir in agents_source_dir.iterdir():
            if agent_dir.is_dir() and (agent_dir / "agent.py").exists():
                try:
                    agent_name = agent_dir.name
                    
                    # Import the agent class
                    module_name = f"agents.{agent_name}.agent"
                    spec = importlib.util.spec_from_file_location(module_name, agent_dir / "agent.py")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find the agent config class
                    agent_class = None
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (hasattr(attr, 'get_config') and hasattr(attr, 'get_name') and 
                            hasattr(attr, 'get_type') and callable(attr.get_config)):
                            agent_class = attr
                            break
                    
                    if agent_class:
                        # Get configuration
                        config = agent_class.get_config()
                        
                        # Create target directory and save JSON
                        target_agent_dir = agents_target_dir / agent_name
                        target_agent_dir.mkdir(exist_ok=True)

                        with open(target_agent_dir / "agent.json", 'w') as f:
                            json.dump(config, f, indent=2)
                        
                        print(f"  ✅ {agent_name}")
                    else:
                        print(f"  ❌ No agent class found in {agent_name}")
                        
                except Exception as e:
                    print(f"  ❌ Failed to convert {agent_dir.name}: {e}")
    
    def convert_messages(self):
        """Convert message Python code back to JSON configs"""
        print("\n💬 Converting messages...")
        
        messages_source_dir = self.source_dir / "messages"
        messages_target_dir = self.target_dir / "messages"
        messages_target_dir.mkdir(exist_ok=True)
        
        if not messages_source_dir.exists():
            return
            
        for message_dir in messages_source_dir.iterdir():
            if message_dir.is_dir() and (message_dir / "message.py").exists():
                try:
                    message_name = message_dir.name
                    
                    # Import the message class
                    module_name = f"messages.{message_name}.message"
                    spec = importlib.util.spec_from_file_location(module_name, message_dir / "message.py")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find the message config class
                    message_class = None
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (hasattr(attr, 'get_config') and hasattr(attr, 'get_name') and 
                            hasattr(attr, 'get_type') and callable(attr.get_config)):
                            message_class = attr
                            break
                    
                    if message_class:
                        # Get content
                        content = message_class.get_config()

                        # Create target directory and save files
                        target_message_dir = messages_target_dir / message_name
                        target_message_dir.mkdir(exist_ok=True)

                        # Get meta configuration if available
                        meta_config = {"type": "message"}  # Default fallback
                        if hasattr(message_class, 'get_meta_config'):
                            try:
                                meta_config = message_class.get_meta_config()
                            except Exception as e:
                                print(f"    ⚠️ Could not get meta config for {message_name}, using default: {e}")

                        # Save meta.json
                        with open(target_message_dir / "meta.json", 'w') as f:
                            json.dump(meta_config, f, indent=2)

                        # Save content as markdown
                        with open(target_message_dir / "message.md", 'w') as f:
                            f.write(content)
                        
                        print(f"  ✅ {message_name}")
                    else:
                        print(f"  ❌ No message class found in {message_name}")
                        
                except Exception as e:
                    print(f"  ❌ Failed to convert {message_dir.name}: {e}")
    
    def convert_tools(self):
        """Convert tool Python code back to JSON configs"""
        print("\n🔧 Converting tools...")
        
        tools_source_dir = self.source_dir / "tools"
        tools_target_dir = self.target_dir / "tools"
        tools_target_dir.mkdir(exist_ok=True)
        
        if not tools_source_dir.exists():
            return
            
        for tool_dir in tools_source_dir.iterdir():
            if tool_dir.is_dir() and (tool_dir / "tool.py").exists():
                try:
                    tool_name = tool_dir.name
                    
                    # Import the tool class
                    module_name = f"tools.{tool_name}.tool"
                    spec = importlib.util.spec_from_file_location(module_name, tool_dir / "tool.py")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find the tool config class
                    tool_class = None
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (hasattr(attr, 'get_config') and hasattr(attr, 'get_name') and 
                            hasattr(attr, 'get_type') and callable(attr.get_config)):
                            tool_class = attr
                            break
                    
                    if tool_class:
                        # Get configuration
                        config = tool_class.get_config()
                        
                        # Create target directory and save JSON
                        target_tool_dir = tools_target_dir / tool_name
                        target_tool_dir.mkdir(exist_ok=True)

                        with open(target_tool_dir / "tool.json", 'w') as f:
                            json.dump(config, f, indent=2)
                        
                        print(f"  ✅ {tool_name}")
                    else:
                        print(f"  ❌ No tool class found in {tool_name}")
                        
                except Exception as e:
                    print(f"  ❌ Failed to convert {tool_dir.name}: {e}")
    
    def convert_prompts(self):
        """Convert prompt Python code back to JSON configs"""
        print("\n📝 Converting prompts...")
        
        prompts_source_dir = self.source_dir / "prompts"
        prompts_target_dir = self.target_dir / "prompts"
        prompts_target_dir.mkdir(exist_ok=True)
        
        if not prompts_source_dir.exists():
            return
            
        for prompt_dir in prompts_source_dir.iterdir():
            if prompt_dir.is_dir() and (prompt_dir / "prompt.py").exists():
                try:
                    prompt_name = prompt_dir.name
                    
                    # Import the prompt class
                    module_name = f"prompts.{prompt_name}.prompt"
                    spec = importlib.util.spec_from_file_location(module_name, prompt_dir / "prompt.py")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find the prompt config class
                    prompt_class = None
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (hasattr(attr, 'get_config') and hasattr(attr, 'get_name') and 
                            callable(attr.get_config)):
                            prompt_class = attr
                            break
                    
                    if prompt_class:
                        # Get content
                        content = prompt_class.get_config()
                        
                        # Create target directory and save markdown
                        target_prompt_dir = prompts_target_dir / prompt_name
                        target_prompt_dir.mkdir(exist_ok=True)

                        with open(target_prompt_dir / "message_0.md", 'w') as f:
                            f.write(content)
                        
                        print(f"  ✅ {prompt_name}")
                    else:
                        print(f"  ❌ No prompt class found in {prompt_name}")
                        
                except Exception as e:
                    print(f"  ❌ Failed to convert {prompt_dir.name}: {e}")
    
    def convert_workflows(self):
        """Convert workflow Python code back to JSON configs"""
        print("\n🔄 Converting workflows...")

        workflows_source_dir = self.source_dir / "workflows"
        workflows_target_dir = self.target_dir / "workflows"
        workflows_target_dir.mkdir(exist_ok=True)

        if not workflows_source_dir.exists():
            return

        for workflow_dir in workflows_source_dir.iterdir():
            if workflow_dir.is_dir() and (workflow_dir / "workflow.py").exists():
                try:
                    workflow_name = workflow_dir.name

                    # Import the workflow class
                    module_name = f"workflows.{workflow_name}.workflow"
                    spec = importlib.util.spec_from_file_location(module_name, workflow_dir / "workflow.py")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find the workflow config class
                    workflow_class = None
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (hasattr(attr, 'get_config') and hasattr(attr, 'get_name') and
                            callable(attr.get_config)):
                            workflow_class = attr
                            break

                    if workflow_class:
                        # Get configuration
                        config = workflow_class.get_config()

                        # Enhance workflow with retry and fail transitions
                        enhanced_config = self._enhance_workflow_with_transitions(config)

                        # Save JSON directly in workflows directory
                        with open(workflows_target_dir / f"{workflow_name}.json", 'w') as f:
                            json.dump(enhanced_config, f, indent=2)

                        print(f"  ✅ {workflow_name} (enhanced with retry/fail transitions)")
                    else:
                        print(f"  ❌ No workflow class found in {workflow_name}")

                except Exception as e:
                    print(f"  ❌ Failed to convert {workflow_dir.name}: {e}")

    def _create_retry_transition(self, state_name):
        """Create a retry transition for a given state"""
        return {
            "name": 'retry',
            "next": state_name,
            "manual": True
        }

    def _create_fail_transition(self, state_name):
        """Create a fail transition for a given state"""
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

    def _enhance_workflow_with_transitions(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance workflow configuration with retry and fail transitions for each state"""
        if 'states' not in config:
            return config

        enhanced_config = config.copy()
        enhanced_states = {}

        # Process each existing state
        for state_name, state_config in config['states'].items():
            # Copy the original state
            enhanced_state = state_config.copy()

            # Get existing transitions or create empty list
            existing_transitions = enhanced_state.get('transitions', [])

            # Add retry and fail transitions
            retry_transition = self._create_retry_transition(state_name)
            fail_transition = self._create_fail_transition(state_name)

            # Combine all transitions
            enhanced_transitions = existing_transitions + [retry_transition, fail_transition]
            enhanced_state['transitions'] = enhanced_transitions

            enhanced_states[state_name] = enhanced_state

            # Create locked state if it doesn't exist
            locked_state_name = f'locked_{state_name}'
            if locked_state_name not in config['states']:
                enhanced_states[locked_state_name] = {
                    "transitions": [
                        {
                            "name": "unlock",
                            "next": state_name,
                            "manual": True
                        }
                    ]
                }

        enhanced_config['states'] = enhanced_states
        return enhanced_config


if __name__ == "__main__":
    converter = CodeToConfigConverter()
    converter.convert_all()
