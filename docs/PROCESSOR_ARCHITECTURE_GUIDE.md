# Processor-Based Workflow Architecture Guide

## 🎯 Overview

This document describes the processor-based workflow architecture that replaces the legacy ChatWorkflow system. The new architecture provides a modular, scalable approach to workflow execution using specialized processors and service-based function organization.

## 🏗️ Architecture Overview

```
Workflow JSON → WorkflowDispatcher → Processor → Service → Function → Result
```

### Core Components

1. **Workflow JSON Files** - Define workflow states, transitions, and processors
2. **WorkflowDispatcher** - Routes workflow execution to appropriate processors
3. **Processors** - Handle specific types of workflow steps (Agent, Function, Message)
4. **Services** - Organize related functions by domain (File Operations, Web Operations, etc.)
5. **Functions** - Individual business logic implementations

## 📁 Project Structure

```
ai_assistant/
├── workflows/                    # Workflow JSON definitions
│   ├── chat_entity.json
│   └── other_workflows.json
├── processors/                   # Processor implementations
│   ├── base_processor.py        # Base processor interface
│   ├── agent_processor.py       # AI agent execution
│   ├── function_processor.py    # Function execution
│   ├── message_processor.py     # Message handling
│   └── loaders/                 # Resource loaders
├── tools/                       # Service-based function organization
│   ├── file_operations_service.py
│   ├── web_operations_service.py
│   ├── state_management_service.py
│   ├── deployment_service.py
│   ├── application_builder_service.py
│   ├── application_editor_service.py
│   ├── workflow_management_service.py
│   ├── workflow_validation_service.py
│   ├── workflow_orchestration_service.py
│   ├── utility_service.py
│   ├── build_id_retrieval_service.py
│   └── github_operations_service.py
├── agents/                      # AI agent configurations
├── prompts/                     # Message templates
├── workflow/                    # Workflow execution engine
│   ├── dispatcher/              # Workflow dispatcher components
│   └── base_workflow.py         # Base workflow classes
└── entity/                      # Entity models and data structures
```

## 🔄 Workflow Execution Flow

### 1. Workflow Definition

Workflows are defined in JSON format with the following structure:

```json
{
  "version": "1.0",
  "name": "workflow_name",
  "desc": "Workflow description",
  "initialState": "none",
  "active": true,
  "states": {
    "state_name": {
      "transitions": [
        {
          "name": "transition_name",
          "next": "next_state",
          "manual": false,
          "processors": [
            {
              "name": "ProcessorType.processor_name",
              "executionMode": "SYNC|ASYNC_NEW_TX",
              "config": {
                "calculationNodesTags": "ai_assistant"
              }
            }
          ],
          "criterion": {
            "type": "function",
            "function": {
              "name": "condition_function_name",
              "config": {
                "calculationNodesTags": "ai_assistant"
              }
            }
          }
        }
      ]
    }
  }
}
```

### 2. Entity Processing in Dispatcher

When an entity is processed in the WorkflowDispatcher:

1. **Entity Retrieval**: Load entity from database using technical_id
2. **Workflow Loading**: Load workflow JSON based on entity.workflow_name
3. **State Resolution**: Determine current state and available transitions
4. **Transition Selection**: Choose transition based on entity state and conditions
5. **Processor Execution**: Execute processors defined in the transition
6. **State Update**: Update entity state based on processor results
7. **Persistence**: Save updated entity back to database

### 3. Processor Types

#### AgentProcessor
- Executes AI agents with prompts and tools
- Handles conversation memory and context
- Supports various AI models (OpenAI, Google ADK)

#### FunctionProcessor  
- Executes business logic functions
- Routes to appropriate service based on function name
- Handles both sync and async function execution

#### MessageProcessor
- Handles user notifications and questions
- Manages message templates and formatting
- Supports different message types (notifications, questions)

## 🛠️ Available Functions (64 Total)

### File Operations (10 functions)
- `save_file`, `read_file`, `save_env_file`
- `get_file_contents`, `get_entity_pojo_contents`
- `list_directory_files`, `clone_repo`, `delete_files`
- `save_entity_templates`, `add_application_resource`

### Web Operations (4 functions)
- `web_search`, `read_link`, `web_scrape`
- `get_cyoda_guidelines`

### State Management (8 functions)
- `finish_discussion`, `is_stage_completed`, `not_stage_completed`
- `is_chat_locked`, `is_chat_unlocked`, `lock_chat`, `unlock_chat`
- `reset_failed_entity`

### Deployment (7 functions)
- `schedule_deploy_env`, `schedule_build_user_application`
- `schedule_deploy_user_application`, `deploy_cyoda_env`
- `deploy_cyoda_env_background`, `deploy_user_application`
- `get_env_deploy_status`

### Application Building (3 functions)
- `build_general_application`, `resume_build_general_application`
- `init_setup_workflow`

### Application Editing (6 functions)
- `edit_existing_app_design_additional_feature`, `edit_api_existing_app`
- `edit_existing_workflow`, `edit_existing_processors`
- `add_new_entity_for_existing_app`, `add_new_workflow`

### Workflow Management (10 functions)
- `launch_gen_app_workflows`, `launch_deployment_chat_workflow`
- `register_workflow_with_app`, `validate_workflow_design`
- `has_workflow_code_validation_succeeded`, `has_workflow_code_validation_failed`
- `save_extracted_workflow_code`, `convert_diagram_to_dataset`
- `convert_workflow_processed_dataset_to_json`, `convert_workflow_json_to_state_diagram`
- `convert_workflow_to_dto`

### Workflow Validation (1 function)
- `validate_workflow_implementation`

### Workflow Orchestration (5 functions)
- `launch_agentic_workflow`, `launch_scheduled_workflow`
- `order_states_in_fsm`, `read_json`, `persist_json`

### Utility (7 functions)
- `get_weather`, `get_humidity`, `get_user_info`
- `init_chats`, `fail_workflow`, `check_scheduled_entity_status`
- `trigger_parent_entity`

### Build ID Retrieval (1 function)
- `get_build_id_from_context`

### GitHub Operations (1 function)
- `add_collaborator`

## 📝 How to Add a New Function

### Step 1: Choose or Create a Service

Determine which service your function belongs to, or create a new service:

```python
# tools/my_new_service.py
from tools.base_service import BaseWorkflowService

class MyNewService(BaseWorkflowService):
    """Service for handling my new functionality."""
    
    async def my_new_function(self, technical_id: str, entity: Any, **kwargs) -> str:
        """
        My new function implementation.
        
        Args:
            technical_id: Technical identifier from workflow context
            entity: Entity object (can be mock or real)
            **kwargs: Additional parameters from workflow_cache
            
        Returns:
            Function result
        """
        # Your implementation here
        return f"Processed {technical_id} successfully"
```

### Step 2: Add Service to FunctionProcessor

Update `processors/function_processor.py`:

```python
# Add import
from tools.my_new_service import MyNewService

# Add to _initialize_services() method
self._services = {
    # ... existing services ...
    'my_new_service': MyNewService(
        workflow_helper_service=mock_workflow_helper,
        entity_service=mock_entity_service,
        cyoda_auth_service=mock_cyoda_auth,
        workflow_converter_service=mock_workflow_converter,
        scheduler_service=mock_scheduler,
        data_service=mock_data_service,
        dataset=mock_dataset,
        mock=True
    ),
}

# Add to function mapping
self._function_map = {
    # ... existing functions ...
    'my_new_function': self._services['my_new_service'].my_new_function,
}
```

### Step 3: Create Tool Definition (Optional)

Create a tool JSON file for AI agents:

```json
// tools/my_new_function.json
{
  "type": "function",
  "function": {
    "name": "my_new_function",
    "description": "Description of what my function does",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {
          "type": "string",
          "description": "First parameter"
        }
      },
      "required": ["param1"]
    }
  }
}
```

### Step 4: Use in Workflows

```json
{
  "processors": [
    {
      "name": "FunctionProcessor.my_new_function",
      "executionMode": "SYNC",
      "config": {
        "calculationNodesTags": "ai_assistant"
      }
    }
  ]
}
```

## 🔧 Function Signature Requirements

All functions should follow this signature pattern:

```python
async def function_name(self, technical_id: str, entity: Any, **kwargs) -> Any:
    """
    Function description.
    
    Args:
        technical_id: Technical identifier from workflow context
        entity: Entity object with attributes like user_id, workflow_cache, etc.
        **kwargs: Additional parameters from workflow_cache or processor config
        
    Returns:
        Function result (any type)
    """
    # Implementation
    pass
```

## 🎯 Best Practices

### Function Development
1. **Single Responsibility**: Each function should have one clear purpose
2. **Error Handling**: Include proper exception handling and logging
3. **Documentation**: Provide clear docstrings with parameter descriptions
4. **Testing**: Write unit tests for all new functions
5. **Async Support**: Use async/await for I/O operations

### Service Organization
1. **Logical Grouping**: Group related functions in the same service
2. **Clear Naming**: Use descriptive service and function names
3. **Dependency Injection**: Use the base service constructor pattern
4. **Mock Support**: Ensure services work with mock dependencies

### Workflow Design
1. **State Management**: Design clear state transitions
2. **Error States**: Include error handling states
3. **Conditional Logic**: Use criteria for complex decision making
4. **Modularity**: Break complex workflows into smaller, reusable components

This architecture provides a scalable, maintainable foundation for workflow-based applications with clear separation of concerns and easy extensibility.

## 🔄 Migration from Legacy Workflows

### Migration Script

The `migrate_workflows.py` script converts legacy Cyoda workflows to the new processor-based architecture:

```bash
# Migrate a single workflow
python migrate_workflows.py old_workflow.json --output-dir ./migrated

# Show what would be migrated (dry run)
python migrate_workflows.py old_workflow.json --dry-run
```

### What the Migration Does

1. **Converts Workflow Schema** - Updates JSON structure to new format
2. **Extracts Inline Agents** - Creates separate agent configuration files
3. **Creates Tool Definitions** - Generates tool JSON files for functions
4. **Migrates Conditions** - Converts conditions to criteria format
5. **Preserves Configuration** - Maintains all original settings and parameters

### Migration Output

```
migrated/
├── workflows/
│   └── workflow_name.json          # Converted workflow
├── agents/
│   └── agent_name/
│       └── agent.json              # Extracted agent configs
├── tools/
│   └── function_name.json          # Function tool definitions
└── messages/
    └── workflow_name/
        └── message_name.md         # Message templates
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific component tests
python tests/run_tests.py --component processors
python tests/run_tests.py --component migration

# Run with coverage
python tests/run_tests.py --coverage

# Interactive test runner
python tests/run_tests.py
```

### Test Categories

1. **Migration Tests** (`test_workflow_migration.py`)
   - Workflow schema conversion
   - Agent extraction
   - Tool creation
   - Condition migration

2. **Processor Tests** (`test_function_processor.py`)
   - Function execution
   - Service initialization
   - Error handling
   - Mock entity creation

3. **Orchestration Tests** (`test_workflow_orchestration.py`)
   - Workflow launching
   - State ordering
   - JSON persistence
   - Async operations

### Test Structure

```
tests/
├── test_workflow_migration.py      # Migration functionality
├── test_function_processor.py      # Function processor tests
├── test_workflow_orchestration.py  # Orchestration service tests
├── tools/                          # Service-specific tests
├── workflow/dispatcher/            # Dispatcher tests
└── run_tests.py                    # Test runner script
```
