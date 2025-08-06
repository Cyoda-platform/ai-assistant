#!/usr/bin/env python3
"""
Workflow Configs to Code Converter

Converts all JSON configurations in workflow_configs/ to Python code in workflow_config_code/
maintaining the same directory structure.

Each generated class implements the appropriate interface:
- Agents: AgentConfig with get_name() and get_config()
- Messages: MessageConfig with get_name() and get_config()  
- Tools: FunctionProcessor and ToolConfig with get_name() and get_config()
- Prompts: PromptConfig with get_name() and get_content()
- Workflows: Function returning workflow configuration
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


class WorkflowConfigConverter:
    """Converts workflow JSON configs to Python code"""
    
    def __init__(self, source_dir: str = "workflow_configs", target_dir: str = "workflow_config_code"):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
    def convert_all(self):
        """Convert all configurations to Python code"""
        print("🔄 CONVERTING WORKFLOW CONFIGS TO CODE")
        print("=" * 40)
        
        if not self.source_dir.exists():
            print(f"❌ Source directory {self.source_dir} does not exist")
            return
            
        # Create target directory and make it a package
        self.target_dir.mkdir(exist_ok=True)
        self._create_init_file(self.target_dir)
        
        # Convert each type
        self._convert_agents()
        self._convert_messages()
        self._convert_tools()
        self._convert_prompts()
        self._convert_workflows()
        
        print(f"\n✅ Conversion complete! Generated code in: {self.target_dir}")
        
    def _convert_agents(self):
        """Convert all agent configurations"""
        agents_dir = self.source_dir / "agents"
        if not agents_dir.exists():
            return
            
        target_agents_dir = self.target_dir / "agents"
        target_agents_dir.mkdir(exist_ok=True)
        self._create_init_file(target_agents_dir)
        
        print("\n📋 Converting agents...")
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                agent_json = agent_dir / "agent.json"
                if agent_json.exists():
                    self._convert_agent_config(agent_json, target_agents_dir / agent_dir.name)
                    
    def _convert_messages(self):
        """Convert all message configurations"""
        messages_dir = self.source_dir / "messages"
        if not messages_dir.exists():
            return
            
        target_messages_dir = self.target_dir / "messages"
        target_messages_dir.mkdir(exist_ok=True)
        self._create_init_file(target_messages_dir)
        
        print("\n💬 Converting messages...")
        for message_dir in messages_dir.iterdir():
            if message_dir.is_dir():
                meta_json = message_dir / "meta.json"
                message_md = message_dir / "message.md"
                if meta_json.exists():
                    self._convert_message_config(meta_json, message_md, target_messages_dir / message_dir.name)
                    
    def _convert_tools(self):
        """Convert all tool configurations"""
        tools_dir = self.source_dir / "tools"
        if not tools_dir.exists():
            return
            
        target_tools_dir = self.target_dir / "tools"
        target_tools_dir.mkdir(exist_ok=True)
        self._create_init_file(target_tools_dir)
        
        print("\n🔧 Converting tools...")
        for tool_dir in tools_dir.iterdir():
            if tool_dir.is_dir():
                tool_json = tool_dir / "tool.json"
                if tool_json.exists():
                    self._convert_tool_config(tool_json, target_tools_dir / tool_dir.name)
                    
    def _convert_prompts(self):
        """Convert all prompt configurations"""
        prompts_dir = self.source_dir / "prompts"
        if not prompts_dir.exists():
            return
            
        target_prompts_dir = self.target_dir / "prompts"
        target_prompts_dir.mkdir(exist_ok=True)
        self._create_init_file(target_prompts_dir)
        
        print("\n📝 Converting prompts...")
        for prompt_dir in prompts_dir.iterdir():
            if prompt_dir.is_dir():
                # Look for message_0.md or any .md file
                md_files = list(prompt_dir.glob("*.md"))
                if md_files:
                    self._convert_prompt_config(md_files[0], target_prompts_dir / prompt_dir.name)
                    
    def _convert_workflows(self):
        """Convert all workflow configurations"""
        workflows_dir = self.source_dir / "workflows"
        if not workflows_dir.exists():
            return
            
        target_workflows_dir = self.target_dir / "workflows"
        target_workflows_dir.mkdir(exist_ok=True)
        self._create_init_file(target_workflows_dir)
        
        print("\n🔄 Converting workflows...")
        for workflow_file in workflows_dir.glob("*.json"):
            self._convert_workflow_config(workflow_file, target_workflows_dir)

    def _convert_agent_config(self, agent_json: Path, target_dir: Path):
        """Convert agent JSON to Python code"""
        try:
            with open(agent_json, 'r') as f:
                config = json.load(f)

            agent_name = self._extract_name_from_path(agent_json.parent.name)
            class_name = self._to_class_name(agent_name, "agent")

            target_dir.mkdir(exist_ok=True)
            self._create_init_file(target_dir)
            target_file = target_dir / "agent.py"

            # Format JSON with proper indentation and class references for Python code
            config_json = self._format_json_with_class_references(config, "agent")

            # Generate imports for referenced classes
            imports = self._generate_imports_for_agent(config)

            # Create config.py file
            config_file = target_dir / "config.py"
            config_code = f'''"""
{class_name} Configuration

Generated from config: {agent_json}
Configuration data for the agent.
"""

from typing import Any, Dict, Callable
{imports}


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get agent configuration factory"""
    return lambda params=None: {config_json}
'''
            self._write_code_file(config_file, config_code)

            # Create main agent.py file
            code = f'''"""
{class_name} Agent

Generated from config: {agent_json}
Implements AgentProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import AgentProcessor
from .config import get_config


class {class_name}(AgentProcessor):
    """Agent configuration for {agent_name}"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return AgentProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{{{class_name}.get_type()}}.{agent_name}"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get agent configuration"""
        config_factory = get_config()
        return config_factory(params or {{}})


# Create singleton instance
{agent_name}_agent = {class_name}()
'''

            self._write_code_file(target_file, code)
            print(f"  ✅ {agent_name}")

        except Exception as e:
            print(f"  ❌ Failed to convert {agent_json}: {e}")

    def _convert_message_config(self, meta_json: Path, message_md: Path, target_dir: Path):
        """Convert message JSON + markdown to Python code"""
        try:
            with open(meta_json, 'r') as f:
                config = json.load(f)

            message_name = self._extract_name_from_path(meta_json.parent.name)
            class_name = self._to_class_name(message_name, "message")

            target_dir.mkdir(exist_ok=True)
            self._create_init_file(target_dir)
            target_file = target_dir / "message.py"

            # Read content from markdown file if it exists
            content = ""
            if message_md.exists():
                with open(message_md, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

            # Create config.py file
            config_file = target_dir / "config.py"
            config_code = f'''"""
{class_name} Configuration

Generated from config: {meta_json}
Configuration data for the message.
"""

from typing import Any, Dict, Callable
import json


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get message configuration factory"""
    return lambda params=None: """{content}"""


def get_meta_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get message meta configuration factory"""
    return lambda params=None: {repr(config)}
'''
            self._write_code_file(config_file, config_code)

            # Create main message.py file
            code = f'''"""
{class_name} Message

Generated from config: {meta_json}
Implements MessageProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import MessageProcessor
from .config import get_config, get_meta_config


class {class_name}(MessageProcessor):
    """Message configuration for {message_name}"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return MessageProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{{{class_name}.get_type()}}.{message_name}"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> str:
        """Get message configuration"""
        config_factory = get_config()
        return config_factory(params or {{}})

    @staticmethod
    def get_meta_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get message meta configuration"""
        meta_factory = get_meta_config()
        return meta_factory(params or {{}})


# Create singleton instance
{message_name}_message = {class_name}()
'''

            self._write_code_file(target_file, code)
            print(f"  ✅ {message_name}")

        except Exception as e:
            print(f"  ❌ Failed to convert {meta_json}: {e}")

    def _convert_tool_config(self, tool_json: Path, target_dir: Path):
        """Convert tool JSON to Python code"""
        try:
            with open(tool_json, 'r') as f:
                config = json.load(f)

            tool_name = self._extract_name_from_path(tool_json.parent.name)
            class_name = self._to_class_name(tool_name, "tool")

            target_dir.mkdir(exist_ok=True)
            self._create_init_file(target_dir)
            target_file = target_dir / "tool.py"

            # Format JSON with proper indentation for Python code
            config_json = self._format_json_for_python(config)

            # Create config.py file
            config_file = target_dir / "config.py"
            config_code = f'''"""
{class_name} Configuration

Generated from config: {tool_json}
Configuration data for the tool.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get tool configuration factory"""
    return lambda params=None: {config_json}
'''
            self._write_code_file(config_file, config_code)

            # Create main tool.py file
            code = f'''"""
{class_name} Tool

Generated from config: {tool_json}
Implements FunctionProcessor interface with get_name() and get_config() methods.
"""

from typing import Any, Dict
from workflow.interfaces.interfaces import FunctionProcessor
from .config import get_config


class {class_name}(FunctionProcessor):
    """Tool configuration for {tool_name}"""

    @staticmethod
    def get_type() -> str:
        """Get the processor type"""
        return FunctionProcessor.get_type()

    @staticmethod
    def get_name() -> str:
        """Get the full processor name"""
        return f"{{{class_name}.get_type()}}.{tool_name}"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get tool configuration"""
        config_factory = get_config()
        return config_factory(params or {{}})

    @staticmethod
    def get_tool_name() -> str:
        """Get the tool name without processor type"""
        return "{tool_name}"


# Create singleton instance
{tool_name}_tool = {class_name}()
'''

            self._write_code_file(target_file, code)
            print(f"  ✅ {tool_name}")

        except Exception as e:
            print(f"  ❌ Failed to convert {tool_json}: {e}")

    def _convert_prompt_config(self, prompt_md: Path, target_dir: Path):
        """Convert prompt markdown to Python code"""
        try:
            prompt_name = self._extract_name_from_path(prompt_md.parent.name)
            class_name = self._to_class_name(prompt_name, "prompt")

            target_dir.mkdir(exist_ok=True)
            self._create_init_file(target_dir)
            target_file = target_dir / "prompt.py"

            # Read content from markdown file
            with open(prompt_md, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # Create config.py file
            config_file = target_dir / "config.py"
            config_code = f'''"""
{class_name} Configuration

Generated from config: {prompt_md}
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """{content}"""
'''
            self._write_code_file(config_file, config_code)

            # Create main prompt.py file
            code = f'''"""
{class_name} Prompt

Generated from config: {prompt_md}
Implements PromptConfig interface with get_name() and get_config() methods.
"""

from .config import get_config
from typing import Any, Dict


class {class_name}:
    """Prompt configuration for {prompt_name}"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this prompt"""
        return "{prompt_name}"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> str:
        """Get prompt configuration"""
        config_factory = get_config()
        return config_factory(params or {{}})


# Create singleton instance
{prompt_name}_prompt = {class_name}()
'''

            self._write_code_file(target_file, code)
            print(f"  ✅ {prompt_name}")

        except Exception as e:
            print(f"  ❌ Failed to convert {prompt_md}: {e}")

    def _convert_workflow_config(self, workflow_json: Path, target_dir: Path):
        """Convert workflow JSON to Python code"""
        try:
            with open(workflow_json, 'r') as f:
                config = json.load(f)

            workflow_name = workflow_json.stem  # Get filename without extension
            class_name = self._to_class_name(workflow_name, "workflow")

            # Create directory for this workflow
            workflow_dir = target_dir / workflow_name
            workflow_dir.mkdir(exist_ok=True)
            self._create_init_file(workflow_dir)
            target_file = workflow_dir / "workflow.py"

            # Format JSON with proper indentation and class references for Python code
            config_json = self._format_json_with_class_references(config, "workflow")

            # Generate imports for workflow
            workflow_imports = self._generate_imports_for_workflow(config)

            # Create config.py file
            config_file = workflow_dir / "config.py"
            config_code = f'''"""
{class_name} Configuration

Generated from config: {workflow_json}
Configuration data for the workflow.
"""

from typing import Any, Dict, Callable
{workflow_imports}


def get_config() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Get workflow configuration factory"""
    return lambda params=None: {config_json}
'''
            self._write_code_file(config_file, config_code)

            # Create main workflow.py file
            code = f'''"""
{class_name} Workflow

Generated from config: {workflow_json}
Workflow configuration with get_name() and get_config() methods.
"""

from typing import Any, Dict
from .config import get_config


class {class_name}:
    """Workflow configuration for {workflow_name}"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this workflow"""
        return "{workflow_name}"

    @staticmethod
    def get_config(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get workflow configuration"""
        config_factory = get_config()
        return config_factory(params or {{}})


# Create singleton instance
{workflow_name}_workflow = {class_name}()
'''

            self._write_code_file(target_file, code)
            print(f"  ✅ {workflow_name}")

        except Exception as e:
            print(f"  ❌ Failed to convert {workflow_json}: {e}")

    def _extract_name_from_path(self, path_name: str) -> str:
        """Extract a clean name from directory/file path"""
        # Use the immediate folder name as-is (this is the actual config name)
        return path_name

    def _to_class_name(self, name: str, config_type: str) -> str:
        """Convert snake_case name to PascalCase class name with proper suffix"""
        # Use the exact folder name, convert to PascalCase
        parts = name.split('_')
        class_name = ''.join(word.capitalize() for word in parts)

        # Add appropriate suffix based on config type
        if config_type == "agent":
            class_name += "AgentConfig"
        elif config_type == "message":
            class_name += "MessageConfig"
        elif config_type == "tool":
            class_name += "ToolConfig"
        elif config_type == "prompt":
            class_name += "PromptConfig"
        elif config_type == "workflow":
            class_name += "WorkflowConfig"

        return class_name

    def _get_class_name_for_reference(self, reference_name: str, config_type: str) -> str:
        """Get the class name that would be generated for a reference"""
        return self._to_class_name(reference_name, config_type)

    def _format_json_with_class_references(self, config: Dict[str, Any], config_type: str) -> str:
        """Format JSON config with class references for tools, messages, and processors"""
        # Deep copy to avoid modifying original
        import copy
        config_copy = copy.deepcopy(config)

        if config_type == "agent":
            # Update tools to use class references
            if "tools" in config_copy:
                for tool in config_copy["tools"]:
                    if "name" in tool:
                        tool_class_name = self._get_class_name_for_reference(tool["name"], "tool")
                        tool["name"] = f"{tool_class_name}.get_tool_name()"

            # Update messages to use class references
            if "messages" in config_copy:
                for message in config_copy["messages"]:
                    if "content_from_file" in message:
                        prompt_class_name = self._get_class_name_for_reference(message["content_from_file"], "prompt")
                        message["content_from_file"] = f"{prompt_class_name}.get_name()"

        elif config_type == "workflow":
            # Update processor references in workflows
            self._update_processor_references(config_copy)

        return self._format_json_for_python(config_copy)

    def _update_processor_references(self, config: Dict[str, Any]):
        """Update processor references in workflow config to use class references"""
        if "states" in config:
            for state_name, state_config in config["states"].items():
                if "transitions" in state_config:
                    for transition in state_config["transitions"]:
                        if "processors" in transition:
                            for processor in transition["processors"]:
                                if "name" in processor:
                                    processor_name = processor["name"]
                                    # Handle AgentProcessor.agent_name format
                                    if processor_name.startswith("AgentProcessor."):
                                        agent_name = processor_name.replace("AgentProcessor.", "")
                                        agent_class_name = self._get_class_name_for_reference(agent_name, "agent")
                                        processor["name"] = f"{agent_class_name}.get_name()"
                                    # Handle FunctionProcessor.function_name format
                                    elif processor_name.startswith("FunctionProcessor."):
                                        function_name = processor_name.replace("FunctionProcessor.", "")
                                        tool_class_name = self._get_class_name_for_reference(function_name, "tool")
                                        processor["name"] = f"{tool_class_name}.get_name()"
                                    # Handle MessageProcessor.message_name format
                                    elif processor_name.startswith("MessageProcessor."):
                                        message_name = processor_name.replace("MessageProcessor.", "")
                                        message_class_name = self._get_class_name_for_reference(message_name, "message")
                                        processor["name"] = f"{message_class_name}.get_name()"

                        # Update criterion function references
                        if "criterion" in transition and "function" in transition["criterion"]:
                            function_config = transition["criterion"]["function"]
                            if "name" in function_config:
                                function_name = function_config["name"]
                                if function_name.startswith("FunctionProcessor."):
                                    tool_name = function_name.replace("FunctionProcessor.", "")
                                    tool_class_name = self._get_class_name_for_reference(tool_name, "tool")
                                    function_config["name"] = f"{tool_class_name}.get_name()"
                                elif function_name.startswith("MessageProcessor."):
                                    message_name = function_name.replace("MessageProcessor.", "")
                                    message_class_name = self._get_class_name_for_reference(message_name, "message")
                                    function_config["name"] = f"{message_class_name}.get_name()"

    def _generate_imports_for_agent(self, config: Dict[str, Any]) -> str:
        """Generate import statements for referenced classes in agent config"""
        imports = []

        # Import tool classes
        if "tools" in config:
            for tool in config["tools"]:
                if "name" in tool:
                    tool_name = tool["name"]
                    tool_class_name = self._get_class_name_for_reference(tool_name, "tool")
                    imports.append(f"from workflow_config_code.tools.{tool_name}.tool import {tool_class_name}")

        # Import prompt classes for messages
        if "messages" in config:
            for message in config["messages"]:
                if "content_from_file" in message:
                    prompt_name = message["content_from_file"]
                    prompt_class_name = self._get_class_name_for_reference(prompt_name, "prompt")
                    imports.append(f"from workflow_config_code.prompts.{prompt_name}.prompt import {prompt_class_name}")

        return "\n".join(imports) if imports else ""

    def _generate_imports_for_workflow(self, config: Dict[str, Any]) -> str:
        """Generate import statements for referenced classes in workflow config"""
        imports = []

        if "states" in config:
            for state_name, state_config in config["states"].items():
                if "transitions" in state_config:
                    for transition in state_config["transitions"]:
                        # Import agent classes from processors
                        if "processors" in transition:
                            for processor in transition["processors"]:
                                if "name" in processor:
                                    processor_name = processor["name"]
                                    if processor_name.startswith("AgentProcessor."):
                                        agent_name = processor_name.replace("AgentProcessor.", "")
                                        agent_class_name = self._get_class_name_for_reference(agent_name, "agent")
                                        imports.append(f"from workflow_config_code.agents.{agent_name}.agent import {agent_class_name}")
                                    elif processor_name.startswith("FunctionProcessor."):
                                        function_name = processor_name.replace("FunctionProcessor.", "")
                                        tool_class_name = self._get_class_name_for_reference(function_name, "tool")
                                        imports.append(f"from workflow_config_code.tools.{function_name}.tool import {tool_class_name}")
                                    elif processor_name.startswith("MessageProcessor."):
                                        message_name = processor_name.replace("MessageProcessor.", "")
                                        message_class_name = self._get_class_name_for_reference(message_name, "message")
                                        imports.append(f"from workflow_config_code.messages.{message_name}.message import {message_class_name}")

                        # Import tool classes from criterion functions
                        if "criterion" in transition and "function" in transition["criterion"]:
                            function_config = transition["criterion"]["function"]
                            if "name" in function_config:
                                function_name = function_config["name"]
                                if function_name.startswith("FunctionProcessor."):
                                    tool_name = function_name.replace("FunctionProcessor.", "")
                                    tool_class_name = self._get_class_name_for_reference(tool_name, "tool")
                                    imports.append(f"from workflow_config_code.tools.{tool_name}.tool import {tool_class_name}")
                                elif function_name.startswith("MessageProcessor."):
                                    message_name = function_name.replace("MessageProcessor.", "")
                                    message_class_name = self._get_class_name_for_reference(message_name, "message")
                                    imports.append(f"from workflow_config_code.messages.{message_name}.message import {message_class_name}")

        # Remove duplicates and return
        return "\n".join(list(set(imports))) if imports else ""

    def _create_init_file(self, directory: Path):
        """Create __init__.py file to make directory a Python package"""
        init_file = directory / "__init__.py"
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write('"""Generated Python package for workflow configurations"""\n')

    def _write_code_file(self, file_path: Path, code: str):
        """Write code to file with proper formatting"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

    def _format_json_for_python(self, config: Dict[str, Any]) -> str:
        """Format JSON config as Python dictionary literal"""
        # Convert to JSON string first, then replace JSON booleans with Python booleans
        json_str = json.dumps(config, indent=8)
        # Replace JSON booleans with Python booleans
        json_str = json_str.replace('true', 'True').replace('false', 'False').replace('null', 'None')

        # Replace quoted class method calls with unquoted ones
        # Pattern: "ClassName.get_name()" -> ClassName.get_name()
        json_str = re.sub(r'"([A-Z][a-zA-Z0-9]*\.get_name\(\))"', r'\1', json_str)
        # Pattern: "ClassName.get_tool_name()" -> ClassName.get_tool_name()
        json_str = re.sub(r'"([A-Z][a-zA-Z0-9]*\.get_tool_name\(\))"', r'\1', json_str)

        return json_str


def main():
    """Main function to run the conversion"""
    converter = WorkflowConfigConverter()
    converter.convert_all()


if __name__ == "__main__":
    main()

    def _convert_tool_config(self, tool_json: Path, target_dir: Path):
        """Convert tool JSON to Python code"""
        try:
            with open(tool_json, 'r') as f:
                config = json.load(f)

            tool_name = self._extract_name_from_path(tool_json.parent.name)
            class_name = self._to_class_name(tool_name)

            target_dir.mkdir(exist_ok=True)
            target_file = target_dir / "tool.py"

            # Extract function configuration
            function_config = config.get('function', {})
            function_name = function_config.get('name', tool_name)
            description = function_config.get('description', 'Tool function')
            parameters = function_config.get('parameters', {})

            # Handle parameters
            properties = parameters.get('properties', {})
            required_params = parameters.get('required', [])

            code = f'''"""
{class_name} Tool

Generated from config: {tool_json}
Implements FunctionProcessor interface with get_config() method.
"""

from typing import Any, Dict
from workflow_best_ux.interfaces import FunctionProcessor, ToolConfig
from workflow_best_ux.builders import tool_config


class {class_name}(FunctionProcessor):
    """{description}"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this tool"""
        return "{function_name}"

    def get_config(self) -> ToolConfig:
        """Get tool configuration"""
        return (tool_config("{function_name}")
                .with_description("{description}")
{self._generate_parameter_additions(properties, required_params)}
                .build())

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the tool function"""
        # TODO: Implement tool execution logic
        return {{"result": "Tool {function_name} executed successfully", "context": context}}


# Create singleton instance
{tool_name}_tool = {class_name}()
'''

            self._write_code_file(target_file, code)
            print(f"  ✅ {tool_name}")

        except Exception as e:
            print(f"  ❌ Failed to convert {tool_json}: {e}")

    def _convert_prompt_config(self, prompt_md: Path, target_dir: Path):
        """Convert prompt markdown to Python code"""
        try:
            prompt_name = self._extract_name_from_path(prompt_md.parent.name)
            class_name = self._to_class_name(prompt_name)

            # Read content from markdown file
            with open(prompt_md, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Escape quotes and newlines for Python string
                content = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

            target_dir.mkdir(exist_ok=True)
            target_file = target_dir / "prompt.py"

            code = f'''"""
{class_name} Prompt

Generated from config: {prompt_md}
Implements PromptConfig interface.
"""

from workflow_best_ux.interfaces import PromptConfig


class {class_name}(PromptConfig):
    """{class_name.replace('Prompt', ' prompt')} configuration"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this prompt"""
        return "{prompt_name}"

    def get_content(self) -> str:
        """Get prompt content"""
        return "{content}"


# Create singleton instance
{prompt_name}_prompt = {class_name}()
'''

            self._write_code_file(target_file, code)
            print(f"  ✅ {prompt_name}")

        except Exception as e:
            print(f"  ❌ Failed to convert {prompt_md}: {e}")
