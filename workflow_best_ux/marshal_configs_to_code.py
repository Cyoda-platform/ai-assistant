"""
Config to Code Marshaller

Reverse operation: marshals JSON configs back into Python code.
Generates code files with proper get_name() and get_config() methods using builders.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List


class ConfigToCodeMarshaller:
    """Marshals JSON configs back to Python code"""
    
    def __init__(self, base_path: str = "workflow_best_ux"):
        self.base_path = Path(base_path)
    
    def marshal_agent_config(self, config_path: str, output_path: str):
        """Marshal agent config JSON to Python code"""
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Extract agent name from config or path
        agent_name = self._extract_agent_name_from_config(config, config_path)
        class_name = self._to_class_name(agent_name)
        
        code = f'''"""
{class_name} Agent

Generated from config: {config_path}
Implements AgentProcessor interface with get_config() method.
"""

from typing import Any, Dict
from workflow_best_ux.interfaces import AgentProcessor, AgentConfig
from workflow_best_ux.builders import agent_config


class {class_name}(AgentProcessor):
    """{class_name.replace('Agent', ' agent')} processor"""
    
    @staticmethod
    def get_name() -> str:
        """Get the static name of this agent processor"""
        return "{agent_name}"
    
    def get_config(self) -> AgentConfig:
        """Get agent configuration"""
        return (agent_config("{agent_name}")
                .with_description("{config.get('description', 'AI agent')}")
                .with_model("{config.get('model', {}).get('model_name', 'gpt-4')}", 
                           temperature={config.get('model', {}).get('temperature', 0.7)}, 
                           max_tokens={config.get('model', {}).get('max_tokens', 4000)})
{self._generate_tool_additions(config.get('tools', []))}
{self._generate_prompt_additions(config.get('messages', []))}
                .build())
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process request using AI agent"""
        # TODO: Implement agent processing logic
        return {{"status": "not_implemented", "agent": "{agent_name}"}}


# Create singleton instance
{agent_name}_agent = {class_name}()
'''
        
        self._write_code_file(output_path, code)
        print(f"✅ Generated agent code: {output_path}")
    
    def marshal_tool_config(self, config_path: str, output_path: str):
        """Marshal tool config JSON to Python code"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Extract tool info from config
        function_config = config.get('function', {})
        tool_name = function_config.get('name', self._extract_name_from_path(config_path, "tool"))
        class_name = self._to_class_name(tool_name)
        description = function_config.get('description', 'Tool function')
        parameters = function_config.get('parameters', {}).get('properties', {})
        required_params = function_config.get('parameters', {}).get('required', [])
        
        code = f'''"""
{class_name} Tool

Generated from config: {config_path}
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
        return "{tool_name}"

    def get_config(self) -> ToolConfig:
        """Get tool configuration"""
        return (tool_config("{tool_name}")
                .with_description("{description}")
{self._generate_parameter_additions(parameters, required_params)}
                .build())

    async def execute(self, **params) -> str:
        """Execute tool function"""
        # TODO: Implement tool execution logic
        return f"Tool {tool_name} executed with params: {{params}}"

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process tool execution as a function processor"""
        # TODO: Implement tool processing logic
        return {{"status": "not_implemented", "tool": "{tool_name}"}}


# Create singleton instance
{tool_name}_tool = {class_name}()
'''
        
        self._write_code_file(output_path, code)
        print(f"✅ Generated tool code: {output_path}")
    
    def marshal_message_config(self, config_path: str, output_path: str, content_file: str = None):
        """Marshal message config JSON to Python code"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        message_name = self._extract_name_from_path(config_path, "message")
        class_name = self._to_class_name(message_name)
        
        # Try to read content from markdown file if provided
        content = "Default message content"
        if content_file and os.path.exists(content_file):
            with open(content_file, 'r') as f:
                content = f.read().strip()
        
        code = f'''"""
{class_name} Message

Generated from config: {config_path}
Implements MessageProcessor interface with get_config() method.
"""

from pathlib import Path
from typing import Any, Dict
from workflow_best_ux.interfaces import MessageProcessor, MessageConfig
from workflow_best_ux.builders import message_config


class {class_name}(MessageProcessor):
    """{class_name.replace('Message', ' message')} processor"""

    @staticmethod
    def get_name() -> str:
        """Get the static name of this message processor"""
        return "{message_name}"

    def __init__(self):
        self.base_path = Path(__file__).parent

    def get_config(self) -> MessageConfig:
        """Get message configuration"""
        content = self.read_content()
        return (message_config("{message_name}")
                .with_content(content)
                .with_type("info")
                .build())

    def read_content(self) -> str:
        """Read the markdown content"""
        md_path = self.base_path / "message.md"
        if md_path.exists():
            return md_path.read_text(encoding='utf-8')
        return "{content}"

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message"""
        # TODO: Implement message processing logic
        return {{"status": "not_implemented", "message": "{message_name}"}}


# Create singleton instance
{message_name}_message = {class_name}()
'''
        
        self._write_code_file(output_path, code)
        print(f"✅ Generated message code: {output_path}")
    
    def marshal_workflow_config(self, config_path: str, output_path: str):
        """Marshal workflow config JSON to Python code"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        workflow_name = config.get('name', self._extract_name_from_path(config_path, "workflow"))
        description = config.get('desc', config.get('description', 'Workflow'))
        initial_state = config.get('initialState', config.get('initial_state', 'none'))
        criterion = config.get('criterion', {})
        states = config.get('states', {})
        
        code = f'''"""
{workflow_name.replace('_', ' ').title()} Workflow

Generated from config: {config_path}
Uses WorkflowBuilder for configuration.
"""

from workflow_best_ux.builders import workflow


def {workflow_name}():
    """
    Build the {workflow_name} using WorkflowBuilder.
    
    Generated from JSON configuration.
    """
    return (workflow("{workflow_name}")
            .with_description("{description}")
            .with_initial_state("{initial_state}")
{self._generate_criterion_config(criterion)}
{self._generate_states_config(states)}
            .build())
'''
        
        self._write_code_file(output_path, code)
        print(f"✅ Generated workflow code: {output_path}")
    
    def _generate_tool_additions(self, tools: List[Dict]) -> str:
        """Generate tool additions for agent config"""
        if not tools:
            return ""
        
        lines = []
        for tool in tools:
            if isinstance(tool, dict) and 'function' in tool:
                tool_name = tool['function'].get('name', 'unknown_tool')
                lines.append(f"                # TODO: Add tool: {tool_name}")
        
        return "\n" + "\n".join(lines) if lines else ""
    
    def _generate_prompt_additions(self, messages: List[Dict]) -> str:
        """Generate prompt additions for agent config"""
        if not messages:
            return ""
        
        lines = []
        for message in messages:
            if isinstance(message, dict) and message.get('role') == 'user':
                content_file = message.get('content_from_file', 'unknown_prompt')
                lines.append(f"                # TODO: Add prompt: {content_file}")
        
        return "\n" + "\n".join(lines) if lines else ""
    
    def _generate_parameter_additions(self, parameters: Dict, required_params: List[str]) -> str:
        """Generate parameter additions for tool config"""
        if not parameters:
            return ""
        
        lines = []
        for param_name, param_info in parameters.items():
            param_type = param_info.get('type', 'string')
            description = param_info.get('description', f'{param_name} parameter')
            required = param_name in required_params
            default = param_info.get('default')
            
            if default is not None:
                lines.append(f'                .add_parameter("{param_name}", "{param_type}", "{description}", required={required}, default={repr(default)})')
            else:
                lines.append(f'                .add_parameter("{param_name}", "{param_type}", "{description}", required={required})')
        
        return "\n" + "\n".join(lines)
    
    def _generate_criterion_config(self, criterion: Dict) -> str:
        """Generate criterion configuration"""
        if not criterion:
            return ""
        
        json_path = criterion.get('jsonPath', criterion.get('json_path', '$.type'))
        operation = criterion.get('operation', 'EQUALS')
        value = criterion.get('value', 'default')
        
        return f'\n            .with_criterion("{json_path}", "{operation}", "{value}")'
    
    def _generate_states_config(self, states: Dict) -> str:
        """Generate states configuration"""
        if not states:
            return ""
        
        lines = []
        for state_name, state_config in states.items():
            description = state_config.get('description', f'{state_name} state')
            lines.append(f'\n            .add_state("{state_name}", "{description}")')
            
            transitions = state_config.get('transitions', [])
            for transition in transitions:
                transition_name = transition.get('name', 'transition')
                next_state = transition.get('next', 'end')
                manual = transition.get('manual', False)
                
                lines.append(f'                .add_transition("{transition_name}")')
                lines.append(f'                    .to("{next_state}")')
                lines.append(f'                    .set_manual({manual})')
                
                processors = transition.get('processors', [])
                for processor in processors:
                    processor_name = processor.get('name', 'unknown_processor')
                    execution_mode = processor.get('execution_mode', 'ASYNC_NEW_TX')
                    lines.append(f'                    .with_processor("{processor_name}", "{execution_mode}")')
        
        return "".join(lines)
    
    def _extract_name_from_path(self, path: str, component_type: str) -> str:
        """Extract component name from file path"""
        path_obj = Path(path)
        if component_type in path_obj.stem:
            return path_obj.stem.replace(f'_{component_type}', '').replace(component_type, '')
        return path_obj.stem.replace('.json', '')
    
    def _to_class_name(self, name: str) -> str:
        """Convert snake_case name to ClassName"""
        parts = name.split('_')
        class_name = ''.join(word.capitalize() for word in parts)
        
        # Add appropriate suffix if not present
        if not class_name.endswith(('Agent', 'Tool', 'Message', 'Prompt')):
            if 'agent' in name.lower():
                class_name += 'Agent'
            elif 'tool' in name.lower():
                class_name += 'Tool'
            elif 'message' in name.lower():
                class_name += 'Message'
            elif 'prompt' in name.lower():
                class_name += 'Prompt'
            else:
                class_name += 'Component'
        
        return class_name
    
    def _write_code_file(self, output_path: str, code: str):
        """Write generated code to file"""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)


def main():
    """Main function to demonstrate config to code marshalling"""
    marshaller = ConfigToCodeMarshaller()
    
    print("🔄 CONFIG TO CODE MARSHALLING")
    print("=" * 35)
    
    # Example usage - marshal existing configs back to code
    config_dir = Path("tests/workflow_best_ux/expected_configs")
    output_dir = Path("workflow_best_ux_generated")
    
    if config_dir.exists():
        # Marshal agent config
        agent_config_path = config_dir / "agent.json"
        if agent_config_path.exists():
            marshaller.marshal_agent_config(
                str(agent_config_path),
                str(output_dir / "agents/chat_assistant/agent.py")
            )
        
        # Marshal tool configs
        tool_configs = [
            ("web_search_tool.json", "tools/web_search/tool.py"),
            ("read_link_tool.json", "tools/read_link/tool.py"),
            ("get_cyoda_guidelines_tool.json", "tools/get_cyoda_guidelines/tool.py"),
            ("get_user_info_tool.json", "tools/get_user_info/tool.py")
        ]
        
        for config_file, output_file in tool_configs:
            config_path = config_dir / config_file
            if config_path.exists():
                marshaller.marshal_tool_config(
                    str(config_path),
                    str(output_dir / output_file)
                )
        
        # Marshal message config
        message_config_path = config_dir / "welcome_message_meta.json"
        if message_config_path.exists():
            marshaller.marshal_message_config(
                str(message_config_path),
                str(output_dir / "messages/welcome_message/message.py")
            )
        
        # Marshal workflow config
        workflow_config_path = config_dir / "workflow.json"
        if workflow_config_path.exists():
            marshaller.marshal_workflow_config(
                str(workflow_config_path),
                str(output_dir / "workflows/simple_chat_workflow/workflow.py")
            )
        
        print(f"\n✅ Generated code files in: {output_dir}")
        print("🎯 All components have proper get_name() and get_config() methods!")
    else:
        print("❌ Config directory not found. Run the marshalling tests first.")


if __name__ == "__main__":
    main()
