# Quick Reference Guide

## 🚀 Getting Started

### Available Processors
- **AgentProcessor.{agent_name}** - Execute AI agents
- **FunctionProcessor.{function_name}** - Execute business functions  
- **MessageProcessor.{message_path}** - Send notifications/questions

### Function Categories (64 total)
```
📁 File Operations (10): save_file, read_file, clone_repo, delete_files...
📁 Web Operations (4): web_search, web_scrape, read_link...
📁 State Management (8): is_chat_locked, finish_discussion, lock_chat...
📁 Deployment (7): deploy_cyoda_env, schedule_deploy_env...
📁 Application Building (3): build_general_application, init_setup_workflow...
📁 Application Editing (6): edit_api_existing_app, add_new_entity_for_existing_app...
📁 Workflow Management (10): convert_workflow_to_dto, validate_workflow_design...
📁 Workflow Orchestration (5): launch_agentic_workflow, persist_json...
📁 Utility (7): get_weather, get_user_info, fail_workflow...
📁 Build ID Retrieval (1): get_build_id_from_context
📁 GitHub Operations (1): add_collaborator
```

## ⚡ Quick Add Function

### 1. Add to Service
```python
# tools/my_service.py
async def my_function(self, technical_id: str, entity: Any, **kwargs) -> str:
    return "result"
```

### 2. Register in FunctionProcessor
```python
# processors/function_processor.py
'my_function': self._services['my_service'].my_function,
```

### 3. Use in Workflow
```json
{
  "processors": [
    {
      "name": "FunctionProcessor.my_function",
      "executionMode": "SYNC",
      "config": {"calculationNodesTags": "ai_assistant"}
    }
  ]
}
```

## 📋 Workflow JSON Template

```json
{
  "version": "1.0",
  "name": "my_workflow",
  "desc": "My workflow description",
  "initialState": "none",
  "active": true,
  "states": {
    "none": {
      "transitions": [
        {
          "name": "start",
          "next": "processing",
          "manual": false,
          "processors": [
            {
              "name": "FunctionProcessor.my_function",
              "executionMode": "SYNC",
              "config": {"calculationNodesTags": "ai_assistant"}
            }
          ]
        }
      ]
    },
    "processing": {
      "transitions": [
        {
          "name": "complete",
          "next": "completed",
          "manual": false,
          "criterion": {
            "type": "function",
            "function": {
              "name": "is_processing_complete",
              "config": {"calculationNodesTags": "ai_assistant"}
            }
          }
        }
      ]
    },
    "completed": {
      "transitions": []
    }
  }
}
```

## 🔧 Common Patterns

### Agent with Tools
```json
{
  "name": "AgentProcessor.my_agent",
  "executionMode": "ASYNC_NEW_TX",
  "config": {"calculationNodesTags": "ai_assistant"}
}
```

### Function with Condition
```json
{
  "name": "process_data",
  "next": "completed",
  "processors": [
    {"name": "FunctionProcessor.process_data", "executionMode": "SYNC"}
  ],
  "criterion": {
    "type": "function",
    "function": {"name": "is_data_valid"}
  }
}
```

### Message Notification
```json
{
  "name": "MessageProcessor.workflow_name/notification_name",
  "executionMode": "SYNC",
  "config": {"calculationNodesTags": "ai_assistant"}
}
```

## 🎯 Entity Processing Flow

```
1. Entity arrives at WorkflowDispatcher
2. Load workflow JSON by entity.workflow_name
3. Find current state and available transitions
4. Execute transition processors in order
5. Check criteria (if present) for next state
6. Update entity state and persist
7. Continue to next transition or wait
```

## 📁 File Locations

- **Workflows**: `workflows/{workflow_name}.json`
- **Agents**: `agents/{agent_name}/agent.json`
- **Tools**: `tools/{tool_name}.json`
- **Messages**: `messages/{workflow_name}/{message_name}.md`
- **Services**: `tools/{service_name}_service.py`
- **Processors**: `processors/{processor_type}_processor.py`

## 🔄 Migration Commands

### Migrate Legacy Workflow
```bash
# Migrate single workflow
python migrate_workflows.py old_workflow.json --output-dir ./migrated

# Dry run (show what would be created)
python migrate_workflows.py old_workflow.json --dry-run
```

### Migration Output
- `workflows/` - Converted workflow JSON
- `agents/` - Extracted agent configurations
- `tools/` - Function tool definitions
- `messages/` - Message templates

## 🧪 Testing Commands

### Run Tests
```bash
# All tests
python tests/run_tests.py

# Specific components
python tests/run_tests.py --component migration
python tests/run_tests.py --component processors

# With coverage
python tests/run_tests.py --coverage

# Interactive mode
python tests/run_tests.py
```

## 🛠️ Development Commands

### Test Function Availability
```bash
python -c "
from processors.function_processor import FunctionProcessor
p = FunctionProcessor()
p._initialize_services()
print(f'Functions: {len(p._function_map)}')
"
```

### Test Processor Import
```bash
python -c "from processors.function_processor import FunctionProcessor; print('✅ OK')"
```

### Check Service Functions
```bash
python -c "
from tools.file_operations_service import FileOperationsService
print([m for m in dir(FileOperationsService) if not m.startswith('_')])
"
```

## 🚨 Common Issues

### Function Not Found
- Check function is in service class
- Verify function is in FunctionProcessor._function_map
- Ensure service is initialized in _initialize_services()

### Import Errors
- Check all required dependencies are installed
- Verify file paths are correct
- Ensure circular imports are avoided

### Workflow Not Executing
- Verify workflow JSON syntax
- Check initialState matches a state name
- Ensure transitions have valid next states

## 📚 Key Files to Know

- `PROCESSOR_ARCHITECTURE_GUIDE.md` - Complete documentation
- `processors/function_processor.py` - Function execution engine
- `workflow/dispatcher/workflow_dispatcher.py` - Workflow orchestration
- `tools/base_service.py` - Base class for all services
- `processors/base_processor.py` - Base class for all processors
