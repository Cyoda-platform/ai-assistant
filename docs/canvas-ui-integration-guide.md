# Canvas UI Integration Guide

## Overview
This guide explains how to integrate the Canvas UI with the backend Canvas Questions API for AI-assisted configuration generation.

**Status:** ✅ **IMPLEMENTED** - Ready for frontend integration

---

## API Endpoint

### Base URL
```
POST /api/v1/chats/canvas-questions
```

### Authentication
Optional - Include `Authorization: Bearer <token>` header if authentication is enabled.

### Implementation Status
- ✅ Endpoint implemented in `routes/chat.py`
- ✅ Service method implemented in `services/chat_service.py`
- ✅ Agent configuration created at `workflow_configs/agents/configs/canvas_assistant/`
- ✅ JSON schemas defined for all response types
- ✅ Hook response wrapper implemented

---

## Request Format

### Request Structure
```typescript
interface CanvasQuestionRequest {
  question: string;                    // Natural language question
  response_type: ResponseType;         // Type of config to generate
  context?: CanvasContext;             // Optional context about the app
}

type ResponseType = 
  | 'entity_json' 
  | 'workflow_json' 
  | 'app_config_json' 
  | 'environment_json';

interface CanvasContext {
  app_name?: string;
  existing_entities?: string[];
  existing_workflows?: string[];
  language?: 'python' | 'java';
  [key: string]: any;                  // Additional context as needed
}
```

### Example Requests

#### 1. Generate Entity
```typescript
const request = {
  question: "Create a Pet entity with name, age, breed, and adoption status",
  response_type: "entity_json",
  context: {
    app_name: "Pet Adoption System",
    existing_entities: ["adopter", "shelter"],
    language: "python"
  }
};

const response = await fetch('/api/v1/chats/canvas-questions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(request)
});
```

#### 2. Generate Workflow
```typescript
const request = {
  question: "Create an adoption workflow with states: pending, approved, completed, rejected",
  response_type: "workflow_json",
  context: {
    app_name: "Pet Adoption System",
    entity_name: "adoption"
  }
};
```

#### 3. Generate App Config
```typescript
const request = {
  question: "Create an app config for a pet adoption system with Pet, Adopter, and Shelter entities",
  response_type: "app_config_json",
  context: {
    language: "python"
  }
};
```

#### 4. Generate Environment
```typescript
const request = {
  question: "Create a production environment configuration",
  response_type: "environment_json",
  context: {
    app_name: "Pet Adoption System"
  }
};
```

---

## Response Format

### Response Structure
```typescript
interface CanvasQuestionResponse {
  message: string;                     // Human-readable explanation
  hook: ResponseHook;                  // UI hook with generated config
}

interface ResponseHook {
  type: HookType;                      // Type of configuration
  action: 'preview';                   // Action to take (always 'preview' for now)
  data: any;                           // Generated configuration object
}

type HookType = 
  | 'entity_config' 
  | 'workflow_config' 
  | 'app_config' 
  | 'environment_config';
```

### Example Responses

#### Entity Response
```json
{
  "message": "I've created a Pet entity with the requested fields including name, age, breed, and adoption status.",
  "hook": {
    "type": "entity_config",
    "action": "preview",
    "data": {
      "name": "pet",
      "version": "1",
      "description": "Represents a pet available for adoption",
      "fields": [
        {
          "name": "name",
          "type": "string",
          "required": true,
          "description": "Pet's name"
        },
        {
          "name": "age",
          "type": "integer",
          "required": true,
          "description": "Pet's age in years"
        },
        {
          "name": "breed",
          "type": "string",
          "required": true,
          "description": "Pet's breed"
        },
        {
          "name": "adoptionStatus",
          "type": "string",
          "enum": ["available", "pending", "adopted"],
          "required": true,
          "description": "Current adoption status"
        }
      ],
      "relationships": [
        {
          "name": "adopter",
          "type": "many-to-one",
          "target": "adopter",
          "description": "The person who adopted this pet"
        }
      ]
    }
  }
}
```

#### Workflow Response
```json
{
  "message": "I've created an adoption workflow with the requested states and transitions.",
  "hook": {
    "type": "workflow_config",
    "action": "preview",
    "data": {
      "name": "adoption_workflow",
      "version": "1.0",
      "description": "Manages the pet adoption process",
      "initialState": "pending",
      "active": true,
      "states": {
        "pending": {
          "transitions": [
            {
              "name": "approve",
              "next": "approved",
              "manual": true,
              "description": "Approve the adoption request"
            },
            {
              "name": "reject",
              "next": "rejected",
              "manual": true,
              "description": "Reject the adoption request"
            }
          ]
        },
        "approved": {
          "transitions": [
            {
              "name": "complete",
              "next": "completed",
              "manual": true,
              "description": "Mark adoption as completed"
            }
          ]
        },
        "completed": {
          "transitions": []
        },
        "rejected": {
          "transitions": []
        }
      }
    }
  }
}
```

#### App Config Response
```json
{
  "message": "I've created an app configuration for your Pet Adoption System with three entities.",
  "hook": {
    "type": "app_config",
    "action": "preview",
    "data": {
      "name": "Pet Adoption System",
      "description": "A system for managing pet adoptions",
      "language": "python",
      "entities": [
        {
          "name": "pet",
          "version": "1",
          "workflows": [
            {"name": "pet_lifecycle", "version": "1.0"}
          ]
        },
        {
          "name": "adopter",
          "version": "1",
          "workflows": [
            {"name": "adopter_registration", "version": "1.0"}
          ]
        },
        {
          "name": "shelter",
          "version": "1",
          "workflows": [
            {"name": "shelter_management", "version": "1.0"}
          ]
        }
      ],
      "environments": [
        {"name": "development", "description": "Development environment"},
        {"name": "staging", "description": "Staging environment"},
        {"name": "production", "description": "Production environment"}
      ]
    }
  }
}
```

#### Environment Response
```json
{
  "message": "I've created a production environment configuration with recommended settings.",
  "hook": {
    "type": "environment_config",
    "action": "preview",
    "data": {
      "name": "production",
      "description": "Production environment",
      "config": {
        "database_url": "postgresql://prod-db:5432/petadoption",
        "api_url": "https://api.petadoption.com",
        "debug": false
      }
    }
  }
}
```

---

## UI Integration Pattern

### 1. User Interaction Flow

```typescript
// User types question in canvas UI
const userQuestion = "Create a Pet entity with name and age";

// Send request to backend
const response = await canvasAPI.askQuestion({
  question: userQuestion,
  response_type: "entity_json",
  context: getCurrentCanvasContext()
});

// Display AI message
displayMessage(response.message);

// Show preview of generated config
if (response.hook) {
  showConfigPreview(response.hook);
}
```

### 2. Preview Component

```typescript
function showConfigPreview(hook: ResponseHook) {
  switch (hook.type) {
    case 'entity_config':
      return <EntityPreview data={hook.data} onApply={applyEntity} />;
    case 'workflow_config':
      return <WorkflowPreview data={hook.data} onApply={applyWorkflow} />;
    case 'app_config':
      return <AppConfigPreview data={hook.data} onApply={applyAppConfig} />;
    case 'environment_config':
      return <EnvironmentPreview data={hook.data} onApply={applyEnvironment} />;
  }
}
```

### 3. Apply to Canvas

```typescript
function applyEntity(entityData: any) {
  // Add entity to canvas state
  canvas.addEntity({
    name: entityData.name,
    version: entityData.version,
    fields: entityData.fields,
    relationships: entityData.relationships
  });
  
  // Update UI
  canvas.render();
  
  // Show success message
  showToast("Entity added to canvas!");
}
```

---

## Error Handling

### Error Response Format
```typescript
interface ErrorResponse {
  error: string;
  details?: {
    field?: string;
    message: string;
    suggestion?: string;
  };
}
```

### Example Error Responses

#### Invalid Response Type
```json
{
  "error": "Invalid request",
  "details": {
    "field": "response_type",
    "message": "Must be one of: entity_json, workflow_json, app_config_json, environment_json"
  }
}
```

#### Generation Failed
```json
{
  "error": "Failed to generate configuration",
  "details": {
    "message": "Could not parse entity structure from question",
    "suggestion": "Please provide more details about the entity fields"
  }
}
```

### Error Handling Code
```typescript
try {
  const response = await canvasAPI.askQuestion(request);
  
  if (response.hook) {
    showConfigPreview(response.hook);
  }
} catch (error) {
  if (error.response?.data?.error) {
    const errorData = error.response.data;
    showError(errorData.error, errorData.details?.message);
    
    if (errorData.details?.suggestion) {
      showSuggestion(errorData.details.suggestion);
    }
  } else {
    showError("Network error", "Please try again");
  }
}
```

---

## Complete Example: React Component

```typescript
import React, { useState } from 'react';

interface CanvasAssistantProps {
  canvasContext: CanvasContext;
  onConfigGenerated: (hook: ResponseHook) => void;
}

export function CanvasAssistant({ canvasContext, onConfigGenerated }: CanvasAssistantProps) {
  const [question, setQuestion] = useState('');
  const [responseType, setResponseType] = useState<ResponseType>('entity_json');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<CanvasQuestionResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('/api/v1/chats/canvas-questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          response_type: responseType,
          context: canvasContext
        })
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.details?.message || error.error);
      }

      const data = await res.json();
      setResponse(data);
      onConfigGenerated(data.hook);
    } catch (error) {
      console.error('Failed to generate config:', error);
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="canvas-assistant">
      <form onSubmit={handleSubmit}>
        <select 
          value={responseType} 
          onChange={(e) => setResponseType(e.target.value as ResponseType)}
        >
          <option value="entity_json">Entity</option>
          <option value="workflow_json">Workflow</option>
          <option value="app_config_json">App Config</option>
          <option value="environment_json">Environment</option>
        </select>

        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask AI to generate a configuration..."
          disabled={loading}
        />

        <button type="submit" disabled={loading || !question}>
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </form>

      {response && (
        <div className="response">
          <p className="message">{response.message}</p>
          <ConfigPreview hook={response.hook} />
        </div>
      )}
    </div>
  );
}
```

---

## Best Practices

### 1. Provide Rich Context
```typescript
// Good - Rich context
const context = {
  app_name: "Pet Adoption System",
  existing_entities: ["pet", "adopter", "shelter"],
  existing_workflows: ["adoption_workflow"],
  language: "python"
};

// Bad - Minimal context
const context = {};
```

### 2. Clear Questions
```typescript
// Good - Specific and clear
"Create a Pet entity with name (string), age (integer), breed (string), and adoptionStatus (enum: available, pending, adopted)"

// Bad - Vague
"Make a pet thing"
```

### 3. Handle Loading States
```typescript
// Show loading indicator
setLoading(true);

// Disable form during request
<button disabled={loading}>Generate</button>

// Clear loading after response
setLoading(false);
```

### 4. Validate Before Applying
```typescript
function applyEntity(entityData: any) {
  // Validate entity doesn't already exist
  if (canvas.hasEntity(entityData.name)) {
    if (!confirm(`Entity "${entityData.name}" already exists. Replace?`)) {
      return;
    }
  }
  
  // Apply to canvas
  canvas.addEntity(entityData);
}
```

---

## Testing the API

### Using cURL

#### Test Entity Generation
```bash
curl -X POST http://localhost:8000/api/v1/chats/canvas-questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Create a Pet entity with name, age, breed, and adoption status",
    "response_type": "entity_json",
    "context": {
      "app_name": "Pet Adoption System",
      "existing_entities": ["adopter", "shelter"],
      "language": "python"
    }
  }'
```

#### Test Workflow Generation
```bash
curl -X POST http://localhost:8000/api/v1/chats/canvas-questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Create an adoption workflow with states: pending, approved, completed, rejected",
    "response_type": "workflow_json",
    "context": {
      "app_name": "Pet Adoption System",
      "entity_name": "adoption"
    }
  }'
```

#### Test App Config Generation
```bash
curl -X POST http://localhost:8000/api/v1/chats/canvas-questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Create an app config for a pet adoption system",
    "response_type": "app_config_json",
    "context": {
      "language": "python"
    }
  }'
```

#### Test Environment Generation
```bash
curl -X POST http://localhost:8000/api/v1/chats/canvas-questions \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Create a production environment configuration",
    "response_type": "environment_json",
    "context": {
      "app_name": "Pet Adoption System"
    }
  }'
```

### Using Python
```python
import requests

url = "http://localhost:8000/api/v1/chats/canvas-questions"

# Test entity generation
response = requests.post(url, json={
    "question": "Create a Pet entity with name, age, and breed",
    "response_type": "entity_json",
    "context": {
        "app_name": "Pet Adoption System",
        "language": "python"
    }
})

print(response.json())
```

### Expected Response Format
```json
{
  "message": "I've created a entity config based on your requirements.",
  "hook": {
    "type": "entity_config",
    "action": "preview",
    "data": {
      "name": "pet",
      "version": "1",
      "fields": [
        {
          "name": "name",
          "type": "string",
          "required": true,
          "description": "Pet's name"
        },
        {
          "name": "age",
          "type": "integer",
          "required": true,
          "description": "Pet's age in years"
        },
        {
          "name": "breed",
          "type": "string",
          "required": true,
          "description": "Pet's breed"
        }
      ],
      "relationships": []
    }
  }
}
```

---

## Summary

### Quick Start Checklist
- [ ] Set up API client with `/api/v1/chats/canvas-questions` endpoint
- [ ] Create request interface with `question`, `response_type`, `context`
- [ ] Handle response with `message` and `hook` structure
- [ ] Implement preview components for each config type
- [ ] Add apply/cancel actions for previewed configs
- [ ] Implement error handling with user-friendly messages
- [ ] Test with all four response types

### Key Points
✅ Stateless API - no chat creation needed
✅ Four response types: entity, workflow, app_config, environment
✅ Always returns preview hook for UI rendering
✅ Rich context improves generation quality
✅ Clear error messages with suggestions

### Backend Implementation
✅ Endpoint: `POST /api/v1/chats/canvas-questions`
✅ Service: `ChatService.submit_canvas_question()`
✅ Agent: `canvas_assistant` with 4 specialized tools
✅ Schemas: JSON schemas for validation
✅ Response: Structured hook format for UI integration

### Next Steps for Frontend
1. Implement API client for canvas-questions endpoint
2. Create preview components for each config type
3. Add apply/edit/cancel actions
4. Test with various questions and contexts
5. Handle errors gracefully with user feedback

