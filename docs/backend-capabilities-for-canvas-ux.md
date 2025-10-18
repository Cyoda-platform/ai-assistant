# Backend Capabilities for Canvas-to-Chat UX

## Overview
This document outlines what the current backend can provide to support the Canvas-to-Chat UX design, based on analysis of the existing codebase architecture.

---

## 🏗️ Current Architecture

### Chat System
The backend uses a **workflow-based chat system** where:
- Each chat is a workflow entity with states and transitions
- User interactions trigger state transitions
- AI agents process requests at specific workflow states
- Responses are stored in chat memory and edge messages

### Key Components
1. **Routes** (`routes/chat.py`) - HTTP endpoints for chat operations
2. **Chat Service** (`services/chat_service.py`) - Business logic for chat management
3. **Workflow Dispatcher** (`workflow/dispatcher/`) - Orchestrates workflow execution
4. **AI Agent Handler** (`workflow/dispatcher/ai_agent_handler.py`) - Manages AI interactions
5. **Config Builder** (`workflow/config_builder.py`) - Builds processor configurations

---

## 📡 Available Endpoints

### Chat Management
```
GET    /api/v1/chats                    - List all chats for user
POST   /api/v1/chats                    - Create new chat (with optional files)
GET    /api/v1/chats/{id}               - Get specific chat
PUT    /api/v1/chats/{id}               - Rename/update chat
DELETE /api/v1/chats/{id}               - Delete chat
```

### Question/Answer Flow
```
POST   /api/v1/chats/text-questions     - Submit simple text question (no workflow)
POST   /api/v1/chats/questions          - Submit question with files
POST   /api/v1/chats/workflow-questions - Submit question with workflow context
POST   /api/v1/chats/{id}/text-answers  - Submit text answer to chat
POST   /api/v1/chats/{id}/answers       - Submit answer with files to chat
```

### Workflow Control
```
POST   /api/v1/chats/{id}/approve       - Approve current state and proceed
POST   /api/v1/chats/{id}/rollback      - Rollback to previous state
```

### File Operations
```
GET    /api/v1/chats/{id}/files/{blob_id} - Download file from chat
```

---

## 🔄 How User Questions Are Answered

### 1. Simple Questions (No Workflow)
**Endpoint:** `POST /api/v1/chats/text-questions` or `POST /api/v1/chats/questions`

**Flow:**
```
User Question → ChatService.submit_question() 
             → AI Agent (OpenAI) with tools
             → Response returned directly
```

**Response Format:**
```json
{
  "message": "AI response text"
}
```

**Capabilities:**
- Direct AI response without workflow state management
- Supports file attachments (multiple files)
- Can use tools/functions if configured
- Can enforce response_format (JSON schema)

---

### 2. Workflow-Based Questions
**Endpoint:** `POST /api/v1/chats/{id}/answers`

**Flow:**
```
User Answer → ChatService.submit_answer()
           → Trigger workflow transition
           → WorkflowDispatcher.process_event()
           → EventProcessor handles action
           → AIAgentHandler.run_ai_agent() (if AI action)
           → Response stored in chat memory
           → Edge message created
```

**Response Format:**
```json
{
  "answer_technical_id": "edge-message-uuid"
}
```

**Capabilities:**
- State-based conversation management
- Memory persistence across interactions
- Tool/function calling during workflow
- Conditional transitions based on criteria
- Background task execution (Auggie CLI)
- File handling and blob storage

---

## 🤖 AI Agent Capabilities

### Configuration Structure
AI agents are configured via workflow JSON with processor configs:

```json
{
  "processors": [
    {
      "name": "AgentProcessor.config_name",
      "executionMode": "ASYNC_NEW_TX",
      "config": {
        "calculationNodesTags": "ai_assistant",
        "responseTimeoutMs": 300000
      }
    }
  ]
}
```

### Agent Config Components
Located in `workflow_configs/agents/configs/{config_name}/`:

1. **Agent Configuration** - Defines AI behavior
2. **Tools** - Functions AI can call
3. **Prompts** - System/user messages
4. **Messages** - Pre-configured message templates

### What AI Can Do

#### 1. Tool/Function Calling
```python
# AI can call registered functions
await method_registry.dispatch_method(
    method_name=function_name,
    entity=entity,
    technical_id=technical_id,
    **parameters
)
```

**Available Function Types:**
- File operations (read, write, delete)
- GitHub operations (clone, commit, push, create branch)
- Workflow management (trigger transitions, update state)
- Application building (generate code, compile, deploy)
- State management (save to workflow_cache)

#### 2. Response Format Control
```python
# Enforce JSON schema for responses
response_format = {
    "name": "schema_name",
    "description": "Schema description",
    "schema": {
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}
```

**Use Cases:**
- Structured data extraction
- Workflow JSON generation
- Entity/field definitions
- Validation responses

#### 3. Memory Management
```python
# Store conversation history with tags
await memory_manager.store_ai_response(
    response=response,
    memory=memory,
    memory_tags=["general", "workflow_specific"]
)

# Retrieve tagged memories
messages = await memory_manager.get_tagged_messages(
    memory_id=entity.memory_id,
    tags=["general"]
)
```

#### 4. UI Function Detection
```python
# AI can return UI-specific responses
if function_name.startswith("ui_"):
    return json.dumps({
        "type": "ui_function",
        "function": function_name,
        **args
    })
```

**Current Implementation:**
- Detects UI function calls
- Returns JSON with type marker
- Frontend can parse and render appropriately

---

## 💾 Data Storage & Retrieval

### Chat Entity Structure
```python
{
    "user_id": "user-uuid",
    "chat_id": "chat-uuid",
    "name": "Chat name",
    "description": "Chat description",
    "workflow_name": "workflow_name",
    "current_state": "state_name",
    "current_transition": "transition_name",
    "workflow_cache": {
        # Key-value storage for workflow data
        "git_branch_id": "branch-123",
        "repository_name": "my-app",
        "build_id": "build-456"
    },
    "chat_flow": {
        "current_flow": [],      # Current conversation
        "finished_flow": []      # Completed messages
    },
    "memory_id": "memory-uuid",
    "locked": false,
    "child_entities": [],
    "scheduled_entities": []
}
```

### Edge Messages
```python
{
    "type": "question" | "answer",
    "edge_message_id": "uuid",
    "publish": true,
    "consumed": false,
    "last_modified": "timestamp",
    "user_id": "user-uuid"
}
```

### File Storage
- Files uploaded via multipart/form-data
- Stored as blobs in Cyoda
- Retrieved via blob_id
- Supports multiple files per message

---

## 🎯 What We Can Provide for Canvas UX

### ✅ Currently Available

#### 1. Structured Question Submission
```typescript
// Frontend can send structured data
POST /api/v1/chats/workflow-questions
{
  question: "Build this app: {...}",
  workflow: "build_general_application_python",
  files: [/* canvas export, diagrams, etc */]
}
```

#### 2. JSON Response Format
```python
# Backend can enforce JSON-only responses
response_format = {
    "schema": {
        "type": "object",
        "properties": {
            "entities": {"type": "array"},
            "workflows": {"type": "array"}
        }
    }
}
```

#### 3. Workflow State Tracking
```python
# Track build progress via workflow states
entity.current_state  # "building", "completed", "failed"
entity.workflow_cache # Store build metadata
```

#### 4. File Handling
- Upload canvas JSON exports
- Download generated files
- Store multiple files per interaction

#### 5. Background Processing
```python
# Long-running tasks (Auggie CLI, builds)
asyncio.create_task(background_task)
# Returns immediately, processes in background
```

---

## 🚧 What Would Need Implementation

### 1. Real-time Progress Updates
**Current:** Polling required to check workflow state
**Needed:** WebSocket/SSE for push notifications

**Approach:**
- Add SSE endpoint: `GET /api/v1/chats/{id}/events`
- Emit events during workflow transitions
- Frontend subscribes and updates UI

### 2. Structured Build Status
**Current:** Generic workflow states
**Needed:** Detailed build progress

**Approach:**
```python
# Store in workflow_cache
entity.workflow_cache["build_status"] = {
    "stage": "generating_entities",
    "progress": 45,
    "message": "Creating Pet entity...",
    "entities_completed": ["pet"],
    "entities_pending": ["adopter", "shelter"]
}
```

### 3. Canvas-Specific Response Types
**Current:** Generic text or JSON responses
**Needed:** Typed responses for canvas actions

**Approach:**
```python
# Add response type detection
if response_format.get("canvas_action"):
    return {
        "type": "canvas_action",
        "action": "add_entity",
        "data": {...},
        "auto_apply": false
    }
```

---

## 📋 Recommended Implementation Strategy

### Phase 1: Minimal Viable Integration (1-2 days)

#### Backend Changes:
1. **Add canvas workflow** (`workflow_configs/configs/canvas_app_builder.json`)
   - States: initial → building → completed/failed
   - Processors for validation, building, error handling

2. **Create canvas agent config** (`workflow_configs/agents/configs/canvas_builder/`)
   - Tools: validate_app_config, build_app, get_build_status
   - Response format: JSON schema for app structure

3. **Add build status to workflow_cache**
   ```python
   entity.workflow_cache["canvas_build"] = {
       "status": "building" | "completed" | "failed",
       "progress": 0-100,
       "current_stage": "entities" | "workflows" | "deployment",
       "error": null | {"message": "...", "field": "..."}
   }
   ```

#### Frontend Integration:
```typescript
// Send canvas data to chat
POST /api/v1/chats
{
  name: "Pet Adoption App",
  description: JSON.stringify(canvasData)
}

// Submit to workflow
POST /api/v1/chats/{id}/answers
{
  answer: "Build this application",
  files: [canvasExport.json]
}

// Poll for status
GET /api/v1/chats/{id}
// Check entity.workflow_cache.canvas_build.status
```

### Phase 2: Enhanced UX (3-5 days)

1. **Add SSE endpoint** for real-time updates
2. **Implement validation hooks** before build
3. **Add incremental update support** (delta changes)
4. **Create deployment status tracking**

### Phase 3: Advanced Features (1-2 weeks)

1. **Multi-stage builds** with detailed progress
2. **Error recovery** and retry mechanisms
3. **Version history** and rollback
4. **Collaborative editing** support

---

## 🔧 Example: Building Canvas App

### Backend Workflow Configuration
```json
{
  "name": "canvas_app_builder",
  "initialState": "initial",
  "states": {
    "initial": {
      "transitions": [{
        "name": "validate_and_build",
        "next": "validating",
        "processors": [{
          "name": "AgentProcessor.validate_canvas_app",
          "config": {
            "tools": ["validate_app_structure"],
            "response_format": {
              "schema": {
                "type": "object",
                "properties": {
                  "valid": {"type": "boolean"},
                  "errors": {"type": "array"}
                }
              }
            }
          }
        }]
      }]
    },
    "validating": {
      "transitions": [
        {
          "name": "start_build",
          "next": "building",
          "criterion": {"jsonPath": "$.valid", "operation": "EQUALS", "value": true}
        },
        {
          "name": "validation_failed",
          "next": "failed",
          "criterion": {"jsonPath": "$.valid", "operation": "EQUALS", "value": false}
        }
      ]
    },
    "building": {
      "transitions": [{
        "name": "build_complete",
        "next": "completed",
        "processors": [{
          "name": "AgentProcessor.build_canvas_app",
          "config": {
            "tools": ["generate_entities", "generate_workflows", "deploy_app"]
          }
        }]
      }]
    }
  }
}
```

### Agent Tool Example
```python
async def generate_entities(entity, technical_id, canvas_data):
    """Generate entities from canvas data"""
    entities = canvas_data.get("entities", [])
    
    # Update progress
    entity.workflow_cache["build_progress"] = {
        "stage": "entities",
        "progress": 0,
        "total": len(entities)
    }
    
    for i, entity_def in enumerate(entities):
        # Generate entity code
        code = generate_entity_code(entity_def)
        
        # Update progress
        entity.workflow_cache["build_progress"]["progress"] = i + 1
        await entity_service.update_item(technical_id, entity)
        
    return f"Generated {len(entities)} entities"
```

---

## 📊 Summary

### What Works Today
✅ Workflow-based chat system
✅ AI agent with tool calling
✅ JSON response format enforcement
✅ File upload/download
✅ State management and caching
✅ Background task execution

### What Needs Work
⚠️ Real-time progress updates (SSE/WebSocket)
⚠️ Structured build status tracking
⚠️ Canvas-specific response types
⚠️ Validation hooks
⚠️ Incremental updates

### Recommended Approach
**Start Simple:** Use existing workflow system with polling
**Iterate:** Add SSE for real-time updates
**Enhance:** Build canvas-specific features incrementally

The current backend architecture is **well-suited** for canvas integration with minimal changes needed for MVP.

