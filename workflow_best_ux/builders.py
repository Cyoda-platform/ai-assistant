"""
Builders for Workflow Best UX

Provides fluent builders for all configuration types:
- WorkflowBuilder: Builds workflows
- AgentConfigBuilder: Builds agent configurations
- ToolConfigBuilder: Builds tool configurations
- MessageConfigBuilder: Builds message configurations
- PromptConfigBuilder: Builds prompt configurations
"""

from typing import Dict, Any, List, Optional
from workflow_best_ux.interfaces import AgentConfig, ToolConfig, MessageConfig, PromptConfig


class WorkflowBuilder:
    """Builder for creating workflows"""
    
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.initial_state = "none"
        self.states = {}
        self.criterion = None
        self.version = "1.0"
        self.active = True
    
    def with_description(self, desc: str) -> "WorkflowBuilder":
        """Set workflow description"""
        self.description = desc
        return self
    
    def with_initial_state(self, state: str) -> "WorkflowBuilder":
        """Set initial state"""
        self.initial_state = state
        return self
    
    def with_criterion(self, json_path: str, operation: str, value: str) -> "WorkflowBuilder":
        """Set workflow criterion"""
        self.criterion = {
            "type": "SIMPLE",
            "jsonPath": json_path,
            "operation": operation,
            "value": value
        }
        return self
    
    def add_state(self, name: str, description: str = "") -> "StateBuilder":
        """Add a state to the workflow"""
        return StateBuilder(self, name, description)
    
    def build(self) -> Dict[str, Any]:
        """Build the workflow"""
        return {
            "version": self.version,
            "name": self.name,
            "desc": self.description,
            "initialState": self.initial_state,
            "active": self.active,
            "criterion": self.criterion,
            "states": self.states
        }


class StateBuilder:
    """Builder for workflow states"""
    
    def __init__(self, workflow_builder: WorkflowBuilder, name: str, description: str = ""):
        self.workflow_builder = workflow_builder
        self.name = name
        self.description = description
        self.transitions = []
    
    def add_transition(self, name: str) -> "TransitionBuilder":
        """Add a transition to this state"""
        return TransitionBuilder(self, name)
    
    def add_state(self, name: str, description: str = "") -> "StateBuilder":
        """Add another state to the workflow"""
        self._finalize_state()
        return self.workflow_builder.add_state(name, description)
    
    def build(self) -> Dict[str, Any]:
        """Build the workflow"""
        self._finalize_state()
        return self.workflow_builder.build()
    
    def _finalize_state(self):
        """Add this state to the workflow"""
        self.workflow_builder.states[self.name] = {
            "description": self.description,
            "transitions": self.transitions
        }


class TransitionBuilder:
    """Builder for state transitions"""
    
    def __init__(self, state_builder: StateBuilder, name: str):
        self.state_builder = state_builder
        self.name = name
        self.next_state = None
        self.manual = False
        self.processors = []
    
    def to(self, next_state: str) -> "TransitionBuilder":
        """Set target state"""
        self.next_state = next_state
        return self
    
    def set_manual(self, is_manual: bool = True) -> "TransitionBuilder":
        """Set manual flag"""
        self.manual = is_manual
        return self
    
    def with_processor(self, processor_name: str, execution_mode: str = "ASYNC_NEW_TX") -> "TransitionBuilder":
        """Add a processor to this transition"""
        self.processors.append({
            "name": processor_name,
            "execution_mode": execution_mode
        })
        return self
    
    def add_transition(self, name: str) -> "TransitionBuilder":
        """Add another transition to the same state"""
        self._finalize_transition()
        return self.state_builder.add_transition(name)
    
    def add_state(self, name: str, description: str = "") -> StateBuilder:
        """Add a new state to the workflow"""
        self._finalize_transition()
        return self.state_builder.add_state(name, description)
    
    def build(self) -> Dict[str, Any]:
        """Build the workflow"""
        self._finalize_transition()
        return self.state_builder.build()
    
    def _finalize_transition(self):
        """Add this transition to the state"""
        self.state_builder.transitions.append({
            "name": self.name,
            "next": self.next_state,
            "manual": self.manual,
            "processors": self.processors
        })


class AgentConfigBuilder:
    """Builder for agent configurations"""
    
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.model_name = "gpt-4"
        self.temperature = 0.7
        self.max_tokens = 4000
        self.tools = []
        self.prompts = []
    
    def with_description(self, desc: str) -> "AgentConfigBuilder":
        """Set agent description"""
        self.description = desc
        return self
    
    def with_model(self, model_name: str, temperature: float = 0.7, max_tokens: int = 4000) -> "AgentConfigBuilder":
        """Set model configuration"""
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        return self
    
    def add_tool(self, tool_config: ToolConfig) -> "AgentConfigBuilder":
        """Add a tool configuration"""
        self.tools.append(tool_config)
        return self
    
    def add_prompt(self, prompt_config: PromptConfig) -> "AgentConfigBuilder":
        """Add a prompt configuration"""
        self.prompts.append(prompt_config)
        return self
    
    def build(self) -> "AgentConfigImpl":
        """Build the agent configuration"""
        return AgentConfigImpl(
            name=self.name,
            description=self.description,
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            tools=self.tools,
            prompts=self.prompts
        )


class ToolConfigBuilder:
    """Builder for tool configurations"""
    
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.parameters = {}
    
    def with_description(self, desc: str) -> "ToolConfigBuilder":
        """Set tool description"""
        self.description = desc
        return self
    
    def add_parameter(self, name: str, param_type: str, description: str, required: bool = False, default=None) -> "ToolConfigBuilder":
        """Add a parameter"""
        param_def = {
            "type": param_type,
            "description": description,
            "required": required
        }
        if default is not None:
            param_def["default"] = default
        self.parameters[name] = param_def
        return self
    
    def build(self) -> "ToolConfigImpl":
        """Build the tool configuration"""
        return ToolConfigImpl(
            name=self.name,
            description=self.description,
            parameters=self.parameters
        )


class MessageConfigBuilder:
    """Builder for message configurations"""
    
    def __init__(self, name: str):
        self.name = name
        self.content = ""
        self.message_type = "info"
    
    def with_content(self, content: str) -> "MessageConfigBuilder":
        """Set message content"""
        self.content = content
        return self
    
    def with_type(self, message_type: str) -> "MessageConfigBuilder":
        """Set message type"""
        self.message_type = message_type
        return self
    
    def build(self) -> "MessageConfigImpl":
        """Build the message configuration"""
        return MessageConfigImpl(
            name=self.name,
            content=self.content,
            message_type=self.message_type
        )


class PromptConfigBuilder:
    """Builder for prompt configurations"""
    
    def __init__(self, name: str):
        self.name = name
        self.content = ""
        self.variables = {}
    
    def with_content(self, content: str) -> "PromptConfigBuilder":
        """Set prompt content"""
        self.content = content
        return self
    
    def add_variable(self, name: str, default_value: str = "") -> "PromptConfigBuilder":
        """Add a template variable"""
        self.variables[name] = default_value
        return self
    
    def build(self) -> "PromptConfigImpl":
        """Build the prompt configuration"""
        return PromptConfigImpl(
            name=self.name,
            content=self.content,
            variables=self.variables
        )


# Configuration implementations
class AgentConfigImpl(AgentConfig):
    """Implementation of AgentConfig"""
    
    def __init__(self, name: str, description: str, model_name: str, temperature: float, max_tokens: int, tools: List[ToolConfig], prompts: List[PromptConfig]):
        self._name = name
        self.description = description
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._tools = tools
        self._prompts = prompts
    
    @staticmethod
    def get_name() -> str:
        return "agent_config"
    
    def get_tools(self) -> List[ToolConfig]:
        return self._tools
    
    def get_prompts(self) -> List[PromptConfig]:
        return self._prompts


class ToolConfigImpl(ToolConfig):
    """Implementation of ToolConfig"""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self._name = name
        self.description = description
        self._parameters = parameters
    
    @staticmethod
    def get_name() -> str:
        return "tool_config"
    
    def get_parameters(self) -> Dict[str, Any]:
        return self._parameters


class MessageConfigImpl(MessageConfig):
    """Implementation of MessageConfig"""
    
    def __init__(self, name: str, content: str, message_type: str):
        self._name = name
        self._content = content
        self.message_type = message_type
    
    @staticmethod
    def get_name() -> str:
        return "message_config"
    
    def get_content(self) -> str:
        return self._content


class PromptConfigImpl(PromptConfig):
    """Implementation of PromptConfig"""
    
    def __init__(self, name: str, content: str, variables: Dict[str, str]):
        self._name = name
        self._content = content
        self.variables = variables
    
    @staticmethod
    def get_name() -> str:
        return "prompt_config"
    
    def get_content(self) -> str:
        return self._content


# Convenience functions
def workflow(name: str) -> WorkflowBuilder:
    """Create a new workflow builder"""
    return WorkflowBuilder(name)


def agent_config(name: str) -> AgentConfigBuilder:
    """Create a new agent config builder"""
    return AgentConfigBuilder(name)


def tool_config(name: str) -> ToolConfigBuilder:
    """Create a new tool config builder"""
    return ToolConfigBuilder(name)


def message_config(name: str) -> MessageConfigBuilder:
    """Create a new message config builder"""
    return MessageConfigBuilder(name)


def prompt_config(name: str) -> PromptConfigBuilder:
    """Create a new prompt config builder"""
    return PromptConfigBuilder(name)
