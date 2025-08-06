# Workflow Best UX Configuration Marshalling Tests

This directory contains comprehensive tests that verify all workflow_best_ux components can be automatically marshalled into their config JSON format.

## Test Coverage

### ✅ **Agent Configuration Marshalling** (`test_agent_config_marshalling.py`)
- Tests `ChatAssistantAgent` can be marshalled to JSON
- Verifies `get_config()` method returns proper `AgentConfig`
- Validates JSON structure with model, tools, and prompts
- Tests static `get_name()` method

### ✅ **Tool Configuration Marshalling** (`test_tool_config_marshalling.py`)
- Tests all tools can be marshalled to JSON:
  - `WebSearchTool`
  - `ReadLinkTool`
  - `GetCyodaGuidelinesTool`
  - `GetUserInfoTool`
- Verifies `get_config()` method returns proper `ToolConfig`
- Validates parameter definitions and requirements
- Tests static `get_name()` methods

### ✅ **Message Configuration Marshalling** (`test_message_config_marshalling.py`)
- Tests `WelcomeMessage` can be marshalled to JSON
- Verifies `get_config()` method returns proper `MessageConfig`
- Validates content loading from markdown files
- Tests message processing functionality

### ✅ **Prompt Configuration Marshalling** (`test_prompt_config_marshalling.py`)
- Tests `AssistantPrompt` can be marshalled to JSON
- Verifies `get_config()` method returns proper `PromptConfig`
- Validates content loading and variable substitution
- Tests template rendering functionality

### ✅ **Workflow Configuration Marshalling** (`test_workflow_config_marshalling.py`)
- Tests `simple_chat_workflow()` can be marshalled to JSON
- Verifies workflow builder produces correct structure
- Validates states, transitions, and processor references
- Tests criterion and execution mode configuration

### ✅ **Complete System Marshalling** (`test_all_config_marshalling.py`)
- Comprehensive integration test for all components
- Tests complete system JSON generation
- Verifies component name consistency
- Validates processor reference integrity

### ✅ **Configuration Completeness** (`test_config_completeness.py`)
- Tests that marshalled configs contain ALL expected data from config files
- Compares against actual JSON config files from workflow_best_ux components
- Ensures marshalled configs have at least the same data (can have more, but not less)
- Validates structure and content completeness

## Key Features Tested

### **Interface Compliance**
- All components implement proper interfaces:
  - `AgentProcessor` with `get_config() -> AgentConfig`
  - `FunctionProcessor` with `get_config() -> ToolConfig`
  - `MessageProcessor` with `get_config() -> MessageConfig`
  - `PromptConfig` interface for prompts

### **JSON Marshalling**
- All components can be converted to JSON automatically
- JSON round-trip preservation (parse → stringify → parse)
- Proper data types and structure validation
- Complete system configuration generation

### **Builder Pattern**
- WorkflowBuilder produces correct JSON structure
- Config builders (AgentConfig, ToolConfig, etc.) work properly
- Fluent API generates valid configurations
- Builder method chaining works correctly

### **Static Methods**
- All components have `get_name()` static methods
- Names are consistent between components and configs
- Processor references in workflows are valid

## Running Tests

### Run All Tests
```bash
python tests/workflow_best_ux/run_tests.py
```

### Run Individual Tests
```bash
python tests/workflow_best_ux/test_agent_config_marshalling.py
python tests/workflow_best_ux/test_tool_config_marshalling.py
python tests/workflow_best_ux/test_message_config_marshalling.py
python tests/workflow_best_ux/test_prompt_config_marshalling.py
python tests/workflow_best_ux/test_workflow_config_marshalling.py
python tests/workflow_best_ux/test_all_config_marshalling.py
```

### Run with pytest
```bash
pytest tests/workflow_best_ux/ -v
```

## Example JSON Output

### Agent Configuration
```json
{
  "type": "agent",
  "name": "chat_assistant",
  "config": {
    "description": "Helpful AI assistant for chat interactions",
    "model": {
      "model_name": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 4000
    },
    "tools": ["web_search", "read_link"],
    "prompts": ["assistant_prompt"]
  }
}
```

### Tool Configuration
```json
{
  "type": "tool",
  "name": "web_search",
  "config": {
    "description": "Search the web using Google Custom Search API",
    "parameters": {
      "query": {
        "type": "string",
        "description": "Search query string",
        "required": true
      }
    }
  }
}
```

### Workflow Configuration
```json
{
  "type": "workflow",
  "name": "simple_chat_workflow",
  "config": {
    "name": "simple_chat_workflow",
    "description": "Simple chat workflow with AI agent processing",
    "initial_state": "none",
    "states": {
      "none": {
        "description": "Initial state",
        "transitions": [
          {
            "name": "initialize_chat",
            "next": "ready",
            "manual": false,
            "processors": [
              {
                "name": "MessageProcessor.welcome_message",
                "execution_mode": "ASYNC_NEW_TX"
              }
            ]
          }
        ]
      }
    }
  }
}
```

## Expected Config Files

The test suite includes actual config files copied from workflow_best_ux components:

- `expected_configs/agent.json` - Expected agent configuration
- `expected_configs/web_search_tool.json` - Expected web search tool configuration
- `expected_configs/read_link_tool.json` - Expected read link tool configuration
- `expected_configs/get_cyoda_guidelines_tool.json` - Expected guidelines tool configuration
- `expected_configs/get_user_info_tool.json` - Expected user info tool configuration
- `expected_configs/welcome_message_meta.json` - Expected message metadata
- `expected_configs/assistant_prompt_meta.json` - Expected prompt metadata
- `expected_configs/workflow.json` - Expected workflow configuration

## Test Results

All tests pass successfully, confirming that:

✅ **Every component** in workflow_best_ux can be marshalled to JSON
✅ **All interfaces** are properly implemented
✅ **Builder pattern** works correctly
✅ **JSON structure** is valid and complete
✅ **Component references** are consistent
✅ **Complete system** can be serialized
✅ **Marshalled configs contain ALL expected data** from config files
✅ **Config completeness** is verified against actual JSON files

## Benefits

1. **Automatic Configuration**: Components automatically generate their JSON configs
2. **Type Safety**: Proper interfaces ensure correct structure
3. **Consistency**: All components follow the same patterns
4. **Validation**: Tests ensure JSON is valid and complete
5. **Integration**: Complete system can be marshalled as one unit
6. **Maintainability**: Changes to components are automatically reflected in JSON

This test suite ensures that the workflow_best_ux system can be fully serialized to JSON configuration files automatically, enabling dynamic configuration generation and system introspection.
