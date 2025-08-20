# Unified AgentProcessor Architecture with Injection Support

This document describes the unified AgentProcessor architecture that merges the duplicate hierarchies and provides AI agent injection capabilities.

## Overview

The refactoring unified two previously separate hierarchies:
1. **Configuration Hierarchy** (`workflow/interfaces/interfaces.py` + `workflow_config_code/*`)
2. **Execution Hierarchy** (`workflow/dispatcher/processors/`)

## Architecture

### Template Method Pattern

```
AgentProcessor (Template)
├── validate_entity()
├── get_chat_memory()
├── execute_agent_logic() [ABSTRACT - implemented by children]
├── update_chat_memory()
└── post_process_response()
```

### Class Hierarchy

```
Processor (ABC)
└── AgentProcessor (Template)
    └── ConfigBasedAgentProcessor
        ├── CompileProjectF6g5AgentConfig
        ├── AnalyzeWorkflowsAndExtractOperations960fAgentConfig
        └── ProcessUserInputAgentConfig
```

## Key Components

### 1. AgentProcessor (Template)
- **Location**: `workflow/dispatcher/processors/agent_processor.py`
- **Purpose**: Template method that handles common workflow, directly extends Processor
- **Workflow**:
  1. Validates entity type (must be AgenticFlowEntity)
  2. Gets chat memory from memory manager
  3. Calls `execute_agent_logic()` (abstract - implemented by children)
  4. Updates chat memory
  5. Post-processes response
- **Features**:
  - Abstract class with `@abstractmethod execute_agent_logic()`
  - Provides `get_type()`, `get_name()`, `get_config()` methods
  - Memory manager injection support
  - Base template for all agent processors

### 2. ConfigBasedAgentProcessor
- **Location**: `workflow/dispatcher/processors/config_based_agent_processor.py`
- **Purpose**: Base class for config-based processors with AI agent injection
- **Features**:
  - Implements `execute_agent_logic()` using `ai_agent_handler`
  - Provides `set_ai_agent_handler()` for injection
  - Supports both `get_name()` and `get_config()` methods
  - Parent for all processors in `workflow_config_code/agents`
  - Handles services context for accessing default `ai_agent_handler`

### 3. Specific Config Processors
- **Examples**: `CompileProjectF6g5AgentConfig`, `AnalyzeWorkflowsAndExtractOperations960fAgentConfig`
- **Purpose**: Specific processors for different tasks
- **Features**:
  - Inherit from `ConfigBasedAgentProcessor`
  - Provide specific `get_name()` and `get_config()` implementations
  - Support AI agent injection per processor type

## Injection Points

### 1. AI Agent Handler Injection

```python
# Default usage (uses ai_agent_handler from services)
processor = CompileProjectF6g5AgentConfig()

# Inject custom AI agent
custom_agent = MyCustomCompilerAgent()
processor = CompileProjectF6g5AgentConfig(ai_agent_handler=custom_agent)

# Or inject after creation
processor.set_custom_ai_agent_handler(custom_agent)
```

### 2. Memory Manager Injection

```python
# Inject custom memory manager
custom_memory = MyCustomMemoryManager()
processor = ConfigBasedAgentProcessor(memory_manager=custom_memory)
```

## Usage Examples

### Basic Usage
```python
from workflow.dispatcher.processors.examples import CompileProjectF6g5AgentConfig

# Create processor
processor = CompileProjectF6g5AgentConfig()

# Get configuration
config = processor.get_config()
name = processor.get_name()  # "AgentProcessor.compile_project_f6g5"
```

### Custom AI Agent Injection
```python
class MyCustomCompilerAgent:
    async def run_ai_agent(self, config, entity, memory, technical_id):
        return "Custom compilation result"

# Inject custom agent
processor = CompileProjectF6g5AgentConfig()
processor.set_custom_ai_agent_handler(MyCustomCompilerAgent())
```

### Different Agents for Different Tasks
```python
# Compilation with specialized agent
compile_processor = CompileProjectF6g5AgentConfig(
    ai_agent_handler=SpecializedCompilerAgent()
)

# Analysis with different agent  
analysis_processor = AnalyzeWorkflowsAndExtractOperations960fAgentConfig(
    ai_agent_handler=AdvancedAnalysisAgent()
)
```

## Interfaces

### MemoryManager Interface
```python
class MemoryManager(ABC):
    @abstractmethod
    async def get_chat_memory(self, memory_id: str) -> ChatMemory:
        pass
    
    @abstractmethod
    async def update_chat_memory(self, memory_id: str, chat_memory: ChatMemory) -> None:
        pass
```

### AI Agent Handler Interface
Any class that implements:
```python
async def run_ai_agent(self, config: Dict[str, Any], entity: AgenticFlowEntity, 
                      memory: ChatMemory, technical_id: str) -> str:
    pass
```

## Benefits

1. **Unified Hierarchy**: Single hierarchy instead of duplicate ones
2. **AI Agent Injection**: Easy injection of custom AI agents per processor
3. **Memory Management Injection**: Pluggable memory management strategies
4. **Template Method**: Common workflow handled automatically
5. **Backward Compatibility**: All existing code continues to work
6. **Type Safety**: Clear interfaces and type hints
7. **Extensibility**: Easy to add new processor types

## Migration Guide

### For Existing Code
No changes needed! The refactoring maintains full backward compatibility.

### For New Custom Agents
1. Create a class with `run_ai_agent()` method
2. Inject it into the desired processor
3. The template method handles the rest

### For New Processors
1. Extend `ConfigBasedAgentProcessor`
2. Implement `get_name()` and `get_config()`
3. Optionally override `execute_agent_logic()` for custom behavior

## Testing

Run the demonstration:
```bash
cd /home/kseniia/IdeaProjects/ai-assistant-2
source .venv/bin/activate
PYTHONPATH=/home/kseniia/IdeaProjects/ai-assistant-2 python workflow/dispatcher/processors/examples/demo_injection.py
```

The existing tests continue to pass, confirming backward compatibility is maintained.
