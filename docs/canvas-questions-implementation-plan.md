# Canvas Questions Implementation Plan

## Overview
Implement a stateless endpoint for AI-assisted canvas configuration generation. Users can request entity, workflow, app config, or environment JSON structures, which are returned with UI hooks for preview/application.

---

## Architecture Decisions

### 1. Stateless Design
- **No chat entity creation** - Each request is independent
- **No memory persistence** - Reduces complexity
- **Context passed in request** - All needed info in payload
- **Rationale:** Canvas is the source of truth, not chat history

### 2. Response Hook Structure
```json
{
  "message": "Human-readable explanation",
  "hook": {
    "type": "entity_config" | "workflow_config" | "app_config" | "environment_config",
    "action": "preview",
    "data": { /* Generated config */ }
  }
}
```

### 3. Agent Configuration
- **Dedicated canvas agent** at `workflow_configs/agents/configs/canvas_assistant/`
- **Four specialized tools:**
  - `generate_entity_config`
  - `generate_workflow_config`
  - `generate_app_config`
  - `generate_environment_config`
- **Response format:** Enforced JSON schema per response_type

### 4. Schema Definitions
Located at `workflow_configs/agents/configs/canvas_assistant/schemas/`:
- `entity_schema.json`
- `workflow_schema.json`
- `app_config_schema.json`
- `environment_schema.json`

---

## Implementation Details

### Endpoint Specification

**Route:** `POST /api/v1/chats/canvas-questions`

**Request:**
```json
{
  "question": "Create a Pet entity with name, age, breed, and adoption status",
  "response_type": "entity_json",
  "context": {
    "app_name": "Pet Adoption System",
    "existing_entities": ["adopter", "shelter"],
    "existing_workflows": ["adoption_workflow"],
    "language": "python"
  }
}
```

**Response:**
```json
{
  "message": "I've created a Pet entity with the requested fields and an adoption workflow.",
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
          "target": "adopter"
        }
      ]
    }
  }
}
```

---

## File Structure

```
workflow_configs/agents/configs/canvas_assistant/
├── agent.py                    # Agent configuration
├── tools/
│   ├── generate_entity_config.py
│   ├── generate_workflow_config.py
│   ├── generate_app_config.py
│   └── generate_environment_config.py
├── prompts/
│   └── system_prompt.md
└── schemas/
    ├── entity_schema.json
    ├── workflow_schema.json
    ├── app_config_schema.json
    └── environment_schema.json
```

---

## Schema Definitions

### Entity Schema
```json
{
  "type": "object",
  "required": ["name", "version", "fields"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Entity name in camelCase"
    },
    "version": {
      "type": "string",
      "default": "1"
    },
    "description": {
      "type": "string"
    },
    "fields": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "type"],
        "properties": {
          "name": {"type": "string"},
          "type": {"type": "string", "enum": ["string", "integer", "boolean", "date", "array", "object"]},
          "required": {"type": "boolean", "default": false},
          "description": {"type": "string"},
          "enum": {"type": "array"},
          "default": {}
        }
      }
    },
    "relationships": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "type", "target"],
        "properties": {
          "name": {"type": "string"},
          "type": {"type": "string", "enum": ["one-to-one", "one-to-many", "many-to-one", "many-to-many"]},
          "target": {"type": "string"}
        }
      }
    }
  }
}
```

### Workflow Schema
```json
{
  "type": "object",
  "required": ["name", "version", "initialState", "states"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Workflow name"
    },
    "version": {
      "type": "string",
      "default": "1.0"
    },
    "description": {
      "type": "string"
    },
    "initialState": {
      "type": "string"
    },
    "active": {
      "type": "boolean",
      "default": true
    },
    "states": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["transitions"],
        "properties": {
          "transitions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "next"],
              "properties": {
                "name": {"type": "string"},
                "next": {"type": "string"},
                "manual": {"type": "boolean", "default": false},
                "description": {"type": "string"}
              }
            }
          }
        }
      }
    }
  }
}
```

### App Config Schema
```json
{
  "type": "object",
  "required": ["name", "entities", "environments"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Application name"
    },
    "description": {
      "type": "string"
    },
    "language": {
      "type": "string",
      "enum": ["python", "java"],
      "default": "python"
    },
    "entities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "version"],
        "properties": {
          "name": {"type": "string"},
          "version": {"type": "string"},
          "workflows": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "version"],
              "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"}
              }
            }
          }
        }
      }
    },
    "environments": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name"],
        "properties": {
          "name": {"type": "string"},
          "description": {"type": "string"}
        }
      }
    }
  }
}
```

### Environment Schema
```json
{
  "type": "object",
  "required": ["name"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Environment name (e.g., dev, staging, prod)"
    },
    "description": {
      "type": "string"
    },
    "config": {
      "type": "object",
      "properties": {
        "database_url": {"type": "string"},
        "api_url": {"type": "string"},
        "debug": {"type": "boolean", "default": false}
      }
    }
  }
}
```

---

## Implementation Steps

### Step 1: Create Schemas
Create JSON schema files in `workflow_configs/agents/configs/canvas_assistant/schemas/`

### Step 2: Create Agent Tools
Implement four tools that return structured configs:
- Each tool accepts `question` and `context`
- Returns JSON matching the schema
- Includes helpful descriptions

### Step 3: Create Agent Configuration
- System prompt: "You are a helpful assistant for generating application configurations"
- Tools: All four generation tools
- Response format: Dynamic based on response_type

### Step 4: Implement Endpoint
In `routes/chat.py`:
- Add `POST /api/v1/chats/canvas-questions`
- Validate request (question, response_type, context)
- Call AI agent with appropriate response_format
- Wrap response with hook structure
- Return JSON

### Step 5: Add Service Method
In `services/chat_service.py`:
- `submit_canvas_question(question, response_type, context)`
- Select schema based on response_type
- Call AI agent with schema
- Parse and validate response
- Return with hook wrapper

---

## Response Type Mapping

| response_type | Schema | Hook Type | Tool Called |
|--------------|--------|-----------|-------------|
| `entity_json` | entity_schema.json | entity_config | generate_entity_config |
| `workflow_json` | workflow_schema.json | workflow_config | generate_workflow_config |
| `app_config_json` | app_config_schema.json | app_config | generate_app_config |
| `environment_json` | environment_schema.json | environment_config | generate_environment_config |

---

## Error Handling

### Validation Errors
```json
{
  "error": "Invalid request",
  "details": {
    "field": "response_type",
    "message": "Must be one of: entity_json, workflow_json, app_config_json, environment_json"
  }
}
```

### AI Generation Errors
```json
{
  "error": "Failed to generate configuration",
  "details": {
    "message": "Could not parse entity structure from question",
    "suggestion": "Please provide more details about the entity fields"
  }
}
```

---

## Testing Strategy

### Unit Tests
- Schema validation
- Tool functions
- Hook wrapper logic

### Integration Tests
- Full endpoint flow
- Different response_types
- Error scenarios

### Example Test Cases
1. Generate simple entity with 3 fields
2. Generate workflow with 5 states
3. Generate app config with 3 entities
4. Generate environment config
5. Invalid response_type
6. Missing required context
7. Malformed question

---

## Future Enhancements

### Phase 2
- Support multiple hooks in one response
- Add `apply` action (auto-apply to canvas)
- Validation against existing configs
- Suggestions for improvements

### Phase 3
- Batch generation (multiple entities at once)
- Relationship inference
- Workflow optimization suggestions
- Code generation preview

---

## Timeline

- **Day 1:** Schemas + Agent Config + Tools (4-6 hours)
- **Day 2:** Endpoint + Service + Hook Wrapper (4-6 hours)
- **Day 3:** Tests + Documentation (2-4 hours)

**Total:** 2-3 days for complete implementation

