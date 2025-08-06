# Config Builder

A comprehensive configuration builder for workflow processors that handles three types of processors: `AgentProcessor`, `FunctionProcessor`, and `MessageProcessor`.

## Overview

The Config Builder takes processor names in the format `ProcessorType.config_name` and builds complete configurations by:

1. **AgentProcessor**: Loads agent config and resolves tool/prompt references
2. **FunctionProcessor**: Returns tool configuration directly  
3. **MessageProcessor**: Builds config from message directory structure

## Directory Structure

The config builder expects the following directory structure under `workflow_configs/`:

```
workflow_configs/
├── agents/
│   └── {agent_name}/
│       └── agent.json
├── tools/
│   └── {tool_name}/
│       └── tool.json
├── prompts/
│   └── {prompt_name}/
│       ├── message_0.md
│       ├── message_1.md
│       └── ...
└── messages/
    └── {message_name}/
        ├── message.md
        └── meta.json
```

## Usage

### Basic Usage

```python
from workflow.config_builder import build_processor_config

# Build agent configuration
agent_config = build_processor_config("AgentProcessor.submit_answer_5607")

# Build function configuration  
function_config = build_processor_config("FunctionProcessor.add_new_workflow")

# Build message configuration
message_config = build_processor_config("MessageProcessor.submit_answer_5607")
```

### Advanced Usage

```python
from workflow.config_builder import ConfigBuilder

# Create builder with custom path
builder = ConfigBuilder("custom/workflow_configs")

# Build configuration
config = builder.build_config("AgentProcessor.my_agent")
```

## Processor Types

### 1. AgentProcessor

**Input**: `AgentProcessor.{agent_name}`

**Process**:
1. Loads `workflow_configs/agents/{agent_name}/agent.json`
2. Resolves tool references by replacing `{"name": "tool_name"}` with full tool configs from `workflow_configs/tools/{tool_name}/tool.json`
3. Resolves prompt references by replacing `"content_from_file": "prompt_name"` with actual content from `workflow_configs/prompts/{prompt_name}/`

**Example Input**:
```json
{
  "type": "agent",
  "tools": [
    {"name": "get_user_info"}
  ],
  "messages": [
    {
      "role": "user", 
      "content_from_file": "submit_answer_b8b2"
    }
  ]
}
```

**Example Output**:
```json
{
  "type": "agent",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_user_info",
        "description": "Use this tool to get user information...",
        "parameters": {...}
      }
    }
  ],
  "messages": [
    {
      "role": "user",
      "content": "Hello! You are a very helpful Cyoda assistant..."
    }
  ]
}
```

### 2. FunctionProcessor

**Input**: `FunctionProcessor.{function_name}`

**Process**:
1. Returns the tool config directly from `workflow_configs/tools/{function_name}/tool.json`

**Example Output**:
```json
{
  "type": "function",
  "function": {
    "name": "add_new_workflow",
    "description": "Launches workflow that is necessary...",
    "strict": true,
    "parameters": {
      "type": "object",
      "properties": {...},
      "required": [...]
    }
  }
}
```

### 3. MessageProcessor

**Input**: `MessageProcessor.{message_name}`

**Process**:
1. Reads content from `workflow_configs/messages/{message_name}/message.md`
2. Reads metadata from `workflow_configs/messages/{message_name}/meta.json`
3. Combines them into a message configuration

**Example Files**:

`message.md`:
```markdown
Your request has been processed successfully.
```

`meta.json`:
```json
{
  "type": "notification",
  "publish": true,
  "allow_anonymous_users": true
}
```

**Example Output**:
```json
{
  "type": "notification",
  "notification": "Your request has been processed successfully.",
  "publish": true,
  "allow_anonymous_users": true
}
```

## Error Handling

The config builder provides comprehensive error handling:

- **Invalid Format**: Raises `ValueError` for processor names without proper format
- **Unknown Processor Type**: Raises `ValueError` for unsupported processor types
- **Missing Files**: Raises `FileNotFoundError` for missing configuration files with detailed debugging information
- **Graceful Degradation**: Logs warnings and keeps original references when optional files are missing
- **Working Directory Independence**: Automatically resolves paths relative to project root, ensuring consistent behavior across different execution contexts (threads, processes, etc.)

## Testing

Run the test suite to verify functionality:

```bash
python test_config_builder.py
```

Run examples to see usage patterns:

```bash
python workflow/config_builder_example.py
```

## Integration

The config builder is designed to integrate seamlessly with workflow processing systems:

```python
def process_workflow_transition(transition):
    for processor in transition.get('processors', []):
        processor_name = processor['name']
        
        # Build the complete configuration
        config = build_processor_config(processor_name)
        
        # Process based on type
        processor_type = processor_name.split('.')[0]
        if processor_type == 'AgentProcessor':
            await handle_agent(config)
        elif processor_type == 'FunctionProcessor':
            await handle_function(config)
        elif processor_type == 'MessageProcessor':
            await handle_message(config)
```

## File Organization

- `workflow/config_builder.py`: Main ConfigBuilder class
- `test_config_builder.py`: Comprehensive test suite
- `workflow/config_builder_example.py`: Usage examples
- `workflow/CONFIG_BUILDER_README.md`: This documentation
