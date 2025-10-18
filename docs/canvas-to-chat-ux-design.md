# Canvas to Chat UX Design

## 🎯 Overall Architecture

```
Canvas (Visual Builder) ↔️ Chat (AI Assistant) ↔️ Backend (Build System) ↔️ Canvas (Live App)
```

## 📋 Design Overview

This document outlines the UX flow for building applications using the visual canvas, AI chat assistant, and backend build system in an iterative cycle.

---

## Phase 1: Requirement Formulation (Canvas → Chat)

### Canvas State
User builds app structure visually:
- App metadata (name, description, language)
- Entities (with fields, types, validations)
- Workflows (states, transitions, actions)
- Environments (deployment targets)

### UX Flow
1. User works in **AppsCanvas** to design their app
2. **"Send to Chat" button** appears when canvas has valid structure
3. Clicking sends a **structured prompt** to chat with:
   - App configuration JSON
   - Entity definitions
   - Workflow definitions
   - User's additional instructions

### Data Structure to Send
```typescript
{
  action: "build_app",
  app_config: {
    name: "Pet Adoption",
    language: "python",
    entities: [...],
    workflows: [...]
  },
  user_message: "Please build this application with REST APIs and validation"
}
```

---

## Phase 2: AI Processing & Build (Chat → Backend)

### Chat Behavior
1. AI receives structured requirement
2. Validates the configuration
3. Asks clarifying questions if needed
4. Sends build request to backend via `/build-app` endpoint
5. Shows progress updates in chat
6. Returns build status + app_id

### Backend Response
```typescript
{
  status: "building" | "completed" | "failed",
  app_id: "app-123",
  progress: 45,
  message: "Generating entity models...",
  entities_built: ["pet", "adopter"],
  workflows_built: ["pet-adoption"]
}
```

---

## Phase 3: Display Built App (Backend → Canvas)

### Hook Mechanism
- Backend sends **WebSocket/SSE event** when build completes
- Or chat polls backend for status
- When complete, chat sends special message:

```typescript
{
  type: "app_built",
  app_id: "app-123",
  entities_data: {
    entities: [...],
    workflows: [...],
    environments: [...]
  }
}
```

### Canvas Behavior
1. Detects `app_built` message type
2. **Automatically switches to "View Mode"**
3. Reloads canvas with backend data
4. Shows **"App Built Successfully"** notification
5. Enables **"Edit" mode** for modifications

---

## Phase 4: Edit & Iterate (Canvas → Chat → Backend)

### Edit Flow
1. User clicks **"Edit"** on any entity/workflow
2. Makes changes in canvas
3. **"Send Changes to Chat"** button appears
4. Sends **delta/diff** to chat:

```typescript
{
  action: "update_app",
  app_id: "app-123",
  changes: {
    entities: {
      modified: ["pet"],  // Changed entities
      added: ["shelter"],  // New entities
      deleted: []
    },
    workflows: {
      modified: ["pet-adoption"]
    }
  },
  user_message: "Add a 'shelter' entity and link it to pets"
}
```

5. AI processes changes
6. Updates backend
7. Canvas reloads with updated data

---

## 🏗️ Implementation Plan

### 1. Canvas Component Architecture

```
AppsCanvas
├── AppBuilder Mode (Editable)
│   ├── EntityEditor
│   ├── WorkflowEditor
│   ├── EnvironmentEditor
│   └── SendToChat Button
│
└── AppViewer Mode (Read-only)
    ├── ReadOnly Entities
    ├── ReadOnly Workflows
    └── Edit Button
```

**Flow:**
- SendToChat Button → ChatBot → AI Processing → Backend Build → WebSocket Event → AppViewer Mode

### 2. State Management

```typescript
// Canvas State
interface AppsCanvasState {
  mode: 'builder' | 'viewer';
  appId: string | null;
  isDirty: boolean;  // Has unsaved changes
  isBuilding: boolean;
  buildProgress: number;
  
  // Data
  appConfig: AppConfig;
  entities: Entity[];
  workflows: Workflow[];
  environments: Environment[];
  
  // Original data (for diff calculation)
  originalData: {
    entities: Entity[];
    workflows: Workflow[];
  };
}
```

### 3. Key Features to Implement

#### A. Send to Chat Button

```typescript
// In AppsCanvas.tsx
const handleSendToChat = () => {
  const message = formatAppRequirement(appConfig, entities, workflows);
  onSendToChat(message);
  
  // Optionally switch to chat view
  setCanvasVisible(false);
};

const formatAppRequirement = (app, entities, workflows) => {
  return `I want to build an application with the following structure:

**App Name:** ${app.name}
**Language:** ${app.language}

**Entities:**
${entities.map(e => `- ${e.name}: ${e.fields.map(f => f.name).join(', ')}`).join('\n')}

**Workflows:**
${workflows.map(w => `- ${w.name} (${w.states.length} states)`).join('\n')}

Please build this application with full CRUD APIs, validation, and database schema.

\`\`\`json
${JSON.stringify({app, entities, workflows}, null, 2)}
\`\`\`
`;
};
```

#### B. Detect App Built Event

```typescript
// In ChatBotView.tsx
useEffect(() => {
  const lastMessage = messages[messages.length - 1];
  
  if (lastMessage?.entities_data?.type === 'app_built') {
    // Show notification
    showNotification('App built successfully!');
    
    // Reload canvas with new data
    setCanvasData(lastMessage.entities_data);
    setCanvasMode('viewer');
    setCanvasVisible(true);
  }
}, [messages]);
```

#### C. Calculate Changes (Diff)

```typescript
const calculateChanges = (original, current) => {
  return {
    entities: {
      added: current.entities.filter(e => 
        !original.entities.find(o => o.id === e.id)
      ),
      modified: current.entities.filter(e => {
        const orig = original.entities.find(o => o.id === e.id);
        return orig && JSON.stringify(orig) !== JSON.stringify(e);
      }),
      deleted: original.entities.filter(e =>
        !current.entities.find(c => c.id === e.id)
      )
    },
    workflows: {
      // Similar logic for workflows
    }
  };
};
```

#### D. Mode Switching

```typescript
// Builder Mode: Full editing capabilities
// Viewer Mode: Read-only with "Edit" button

const AppsCanvas = () => {
  const [mode, setMode] = useState<'builder' | 'viewer'>('builder');
  
  return (
    <div>
      {mode === 'viewer' && (
        <button onClick={() => setMode('builder')}>
          Edit Application
        </button>
      )}
      
      {mode === 'builder' && isDirty && (
        <button onClick={handleSendChanges}>
          Send Changes to Chat
        </button>
      )}
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodesDraggable={mode === 'builder'}
        nodesConnectable={mode === 'builder'}
        elementsSelectable={mode === 'builder'}
      />
    </div>
  );
};
```

---

## 🔄 Complete User Journey

### 1. Start Building
- User opens AppsCanvas
- Adds entities, workflows, environments
- Clicks "Send to Chat"

### 2. AI Builds App
- Chat receives structured requirement
- AI validates and asks questions
- Sends to backend `/build-app`
- Shows progress in chat

### 3. App Ready
- Backend completes build
- Sends webhook/event to frontend
- Canvas auto-reloads in "viewer" mode
- Shows success notification

### 4. User Reviews
- Sees built app in canvas
- Can test via environments
- Reviews generated code (optional)

### 5. User Edits
- Clicks "Edit"
- Modifies entities/workflows
- Clicks "Send Changes to Chat"
- AI processes delta and updates backend

### 6. Iterate
- Repeat steps 2-5 as needed

---

## 🎨 UI/UX Enhancements

### Visual Indicators
- **Builder Mode**: Green border, "Building..." badge
- **Viewer Mode**: Blue border, "Live App" badge
- **Dirty State**: Orange dot, "Unsaved changes"
- **Building**: Progress bar in header

### Notifications
- "App sent to AI for building..."
- "Building in progress (45%)..."
- "App built successfully! ✅"
- "Changes sent to AI..."

### Smart Buttons
- **"Send to Chat"** - only when canvas has valid structure
- **"Send Changes"** - only when isDirty
- **"Edit"** - only in viewer mode
- **"View Live App"** - link to deployed environment

---

## 🤔 Open Questions

1. **Should we support real-time collaboration?** (Multiple users editing same app)
2. **How should we handle conflicts?** (User edits while AI is building)
3. **Should canvas auto-reload or ask user?** (When backend updates)
4. **Do we need version history?** (Undo/redo for canvas changes)
5. **Should we validate before sending to chat?** (Required fields, valid workflows)

---

---

## 🎣 Backend Hooks for Better UX

To provide a seamless experience, the backend needs to send specific hooks/events to the frontend at various stages of the build process.

### Hook Types

#### 1. Build Progress Hook
**When:** During app building process
**Purpose:** Show real-time progress to user

```typescript
{
  type: "build_progress",
  app_id: "app-123",
  progress: 45,
  stage: "generating_entities" | "creating_workflows" | "setting_up_database" | "deploying",
  message: "Generating entity models for 'pet' and 'adopter'...",
  timestamp: "2024-01-15T10:30:00Z"
}
```

**Frontend Action:**
- Update progress bar
- Show current stage message
- Display in chat as system message

---

#### 2. App Built Hook
**When:** App build completes successfully
**Purpose:** Notify user and reload canvas

```typescript
{
  type: "app_built",
  app_id: "app-123",
  status: "success",
  message: "Your application 'Pet Adoption' has been built successfully!",
  entities_data: {
    app_config: {...},
    entities: [...],
    workflows: [...],
    environments: [...]
  },
  deployment_url: "https://pet-adoption.cyoda.app",
  timestamp: "2024-01-15T10:35:00Z"
}
```

**Frontend Action:**
- Show success notification
- Switch canvas to viewer mode
- Reload canvas with entities_data
- Display deployment URL
- Auto-open canvas if closed

---

#### 3. Build Error Hook
**When:** App build fails
**Purpose:** Show error details and allow retry

```typescript
{
  type: "build_error",
  app_id: "app-123",
  status: "failed",
  error: {
    code: "VALIDATION_ERROR",
    message: "Entity 'pet' has invalid field type 'unknownType'",
    field: "entities[0].fields[2].type",
    suggestion: "Use one of: string, number, boolean, date, reference"
  },
  timestamp: "2024-01-15T10:32:00Z"
}
```

**Frontend Action:**
- Show error notification
- Highlight problematic field in canvas
- Suggest fix in chat
- Enable "Fix & Retry" button

---

#### 4. Validation Warning Hook
**When:** Before build starts, during validation
**Purpose:** Warn user about potential issues

```typescript
{
  type: "validation_warning",
  app_id: "app-123",
  warnings: [
    {
      severity: "warning" | "info",
      message: "Entity 'pet' has no unique identifier field",
      suggestion: "Consider adding an 'id' field with type 'uuid'",
      field: "entities[0]"
    },
    {
      severity: "info",
      message: "Workflow 'pet-adoption' has no error handling states",
      suggestion: "Add 'error' and 'cancelled' states for better UX"
    }
  ],
  can_proceed: true,
  timestamp: "2024-01-15T10:28:00Z"
}
```

**Frontend Action:**
- Show warnings in chat
- Highlight fields in canvas (yellow border)
- Ask user: "Proceed anyway?" or "Fix warnings first?"

---

#### 5. Entity Generated Hook
**When:** Individual entity is created/updated
**Purpose:** Show incremental progress

```typescript
{
  type: "entity_generated",
  app_id: "app-123",
  entity: {
    id: "entity-pet-1",
    name: "pet",
    fields: [...],
    generated_files: [
      "src/models/pet.py",
      "src/api/pet_controller.py",
      "tests/test_pet.py"
    ]
  },
  timestamp: "2024-01-15T10:30:15Z"
}
```

**Frontend Action:**
- Update entity node in canvas (add checkmark)
- Show in chat: "✅ Entity 'pet' generated"
- Display generated files (expandable)

---

#### 6. Workflow Generated Hook
**When:** Individual workflow is created/updated
**Purpose:** Show workflow creation progress

```typescript
{
  type: "workflow_generated",
  app_id: "app-123",
  workflow: {
    id: "workflow-pet-adoption",
    name: "pet-adoption",
    entity: "pet",
    states: [...],
    transitions: [...],
    generated_files: [
      "workflows/pet_adoption.json",
      "src/workflows/pet_adoption_handler.py"
    ]
  },
  timestamp: "2024-01-15T10:31:00Z"
}
```

**Frontend Action:**
- Update workflow node in canvas (add checkmark)
- Show in chat: "✅ Workflow 'pet-adoption' generated"
- Enable "View Workflow" button

---

#### 7. Deployment Hook
**When:** App is deployed to environment
**Purpose:** Notify user of live deployment

```typescript
{
  type: "deployment_complete",
  app_id: "app-123",
  environment: "production",
  deployment_url: "https://pet-adoption.cyoda.app",
  api_docs_url: "https://pet-adoption.cyoda.app/docs",
  health_check: "healthy",
  timestamp: "2024-01-15T10:35:30Z"
}
```

**Frontend Action:**
- Show success notification with confetti 🎉
- Display clickable deployment URL
- Add "Open App" button in canvas
- Update environment node status to "active"

---

#### 8. Update Complete Hook
**When:** User's changes are applied
**Purpose:** Confirm changes and reload canvas

```typescript
{
  type: "update_complete",
  app_id: "app-123",
  changes_applied: {
    entities: {
      added: ["shelter"],
      modified: ["pet"],
      deleted: []
    },
    workflows: {
      modified: ["pet-adoption"]
    }
  },
  entities_data: {
    // Updated full data
  },
  timestamp: "2024-01-15T11:00:00Z"
}
```

**Frontend Action:**
- Show "Changes applied successfully"
- Reload canvas with updated data
- Clear dirty state
- Highlight changed nodes (green glow)

---

## 💬 Chat Response Formats

When sending questions to canvas chat, the AI should support different response formats based on the context.

### Response Format Options

#### 1. Text Only (Default)
**Use Case:** General questions, explanations, guidance

```typescript
{
  response_format: "text",
  content: "To add a new entity, click the '+' button in the Entities tab..."
}
```

**Example:**
- User: "How do I add a new entity?"
- AI: Returns helpful text explanation

---

#### 2. JSON Only
**Use Case:** Structured data requests, configuration exports

```typescript
{
  response_format: "json",
  content: {
    entities: [...],
    workflows: [...]
  }
}
```

**Example:**
- User: "Show me the current app configuration"
- AI: Returns JSON object only (no text wrapper)

---

#### 3. Workflow JSON Only
**Use Case:** Workflow-specific requests

```typescript
{
  response_format: "workflow_json",
  content: {
    workflow_id: "workflow-pet-adoption",
    name: "pet-adoption",
    entity: "pet",
    states: [...],
    transitions: [...]
  }
}
```

**Example:**
- User: "Generate a workflow for pet adoption"
- AI: Returns workflow JSON that can be directly imported to canvas

---

#### 4. Entity JSON Only
**Use Case:** Entity-specific requests

```typescript
{
  response_format: "entity_json",
  content: {
    entity_id: "entity-pet-1",
    name: "pet",
    fields: [
      { name: "name", type: "string", required: true },
      { name: "age", type: "number", required: false }
    ]
  }
}
```

**Example:**
- User: "Create a pet entity with name and age fields"
- AI: Returns entity JSON that can be directly added to canvas

---

#### 5. Text + JSON (Hybrid)
**Use Case:** Explanation with structured data

```typescript
{
  response_format: "text_json",
  text: "I've created a pet entity with the following structure:",
  json: {
    entity_id: "entity-pet-1",
    name: "pet",
    fields: [...]
  }
}
```

**Example:**
- User: "Help me design a pet entity"
- AI: Explains the design + provides JSON

---

#### 6. Canvas Action
**Use Case:** Direct canvas manipulation

```typescript
{
  response_format: "canvas_action",
  action: "add_entity" | "update_workflow" | "delete_entity" | "add_environment",
  data: {
    entity: {...}
  },
  auto_apply: true  // Automatically apply to canvas
}
```

**Example:**
- User: "Add a shelter entity"
- AI: Returns action that frontend automatically applies to canvas

---

#### 7. Multiple Options (User Choice)
**Use Case:** When AI suggests multiple solutions

```typescript
{
  response_format: "options",
  message: "I can help you with that in several ways:",
  options: [
    {
      id: "option-1",
      label: "Simple pet entity (3 fields)",
      description: "Basic pet with name, age, breed",
      data: { entity: {...} }
    },
    {
      id: "option-2",
      label: "Advanced pet entity (8 fields)",
      description: "Comprehensive pet with medical history, photos, etc.",
      data: { entity: {...} }
    },
    {
      id: "option-3",
      label: "Custom - let me specify fields",
      description: "I'll ask you about each field",
      data: null
    }
  ]
}
```

**Frontend Action:**
- Display options as clickable cards
- User selects one
- Frontend sends selection back to AI
- AI proceeds with chosen option

---

#### 8. Interactive Form
**Use Case:** Guided entity/workflow creation

```typescript
{
  response_format: "interactive_form",
  form: {
    title: "Create Pet Entity",
    fields: [
      {
        name: "entity_name",
        label: "Entity Name",
        type: "text",
        required: true,
        default: "pet"
      },
      {
        name: "fields",
        label: "Fields",
        type: "array",
        items: {
          name: { type: "text", label: "Field Name" },
          type: { type: "select", options: ["string", "number", "boolean"] },
          required: { type: "checkbox", label: "Required?" }
        }
      }
    ],
    submit_label: "Create Entity"
  }
}
```

**Frontend Action:**
- Render interactive form in chat
- User fills out form
- Frontend sends completed form to AI
- AI generates entity and returns canvas_action

---

## 🎯 Answer Examples with Response Formats

### Example 1: User asks "Create a pet entity"

**AI Response:**
```typescript
{
  response_format: "text_json",
  text: "I've designed a pet entity with essential fields for a pet adoption system:",
  json: {
    entity_id: "entity-pet-1",
    name: "pet",
    version: "1",
    fields: [
      { name: "id", type: "uuid", required: true, primary_key: true },
      { name: "name", type: "string", required: true },
      { name: "species", type: "string", required: true },
      { name: "breed", type: "string", required: false },
      { name: "age", type: "number", required: false },
      { name: "status", type: "string", required: true, default: "available" }
    ]
  },
  canvas_action: {
    action: "add_entity",
    data: { /* same as json above */ },
    auto_apply: false  // Ask user first
  },
  follow_up: "Would you like me to add this entity to your canvas?"
}
```

---

### Example 2: User asks "Show me all workflows"

**AI Response:**
```typescript
{
  response_format: "json",
  content: {
    workflows: [
      {
        id: "workflow-pet-adoption",
        name: "pet-adoption",
        entity: "pet",
        states: ["available", "pending", "adopted"],
        transitions: [...]
      }
    ]
  }
}
```

---

### Example 3: User asks "How do I add validation to a field?"

**AI Response:**
```typescript
{
  response_format: "text",
  content: "To add validation to a field:\n\n1. Click on the entity in the canvas\n2. Select the field you want to validate\n3. Click 'Add Validation' button\n4. Choose validation type (required, min/max, regex, etc.)\n\nFor example, to validate an email field:\n- Type: string\n- Validation: regex\n- Pattern: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
}
```

---

### Example 4: User asks "Generate a complete app for pet adoption"

**AI Response:**
```typescript
{
  response_format: "options",
  message: "I can generate a pet adoption app for you. Choose a template:",
  options: [
    {
      id: "basic",
      label: "Basic Pet Adoption",
      description: "2 entities (Pet, Adopter), 1 workflow, simple CRUD",
      preview: {
        entities: ["pet", "adopter"],
        workflows: ["pet-adoption"],
        estimated_time: "2 minutes"
      }
    },
    {
      id: "advanced",
      label: "Advanced Pet Adoption Platform",
      description: "5 entities (Pet, Adopter, Shelter, Application, Medical Record), 3 workflows",
      preview: {
        entities: ["pet", "adopter", "shelter", "application", "medical_record"],
        workflows: ["pet-adoption", "application-review", "medical-tracking"],
        estimated_time: "5 minutes"
      }
    },
    {
      id: "custom",
      label: "Custom - I'll guide you",
      description: "Let's build it step by step together",
      preview: null
    }
  ]
}
```

---

### Example 5: User asks "Fix the validation error in pet entity"

**AI Response:**
```typescript
{
  response_format: "canvas_action",
  text: "I found the issue - the 'age' field has an invalid type. I'll fix it for you:",
  action: "update_entity",
  data: {
    entity_id: "entity-pet-1",
    changes: {
      fields: [
        {
          name: "age",
          type: "number",  // Changed from "unknownType"
          required: false
        }
      ]
    }
  },
  auto_apply: true,
  confirmation: "✅ Fixed: Changed 'age' field type from 'unknownType' to 'number'"
}
```

---

## 📝 Next Steps

1. Implement mode switching (builder/viewer) in AppsCanvas
2. Add "Send to Chat" button with structured message formatting
3. Implement app_built event detection in ChatBotView
4. Add diff calculation for change tracking
5. Implement WebSocket/SSE for build progress updates
6. Add visual indicators and notifications
7. Create validation logic for canvas data
8. **Implement backend hooks system (build_progress, app_built, etc.)**
9. **Add response format handling in chat UI**
10. **Create interactive form renderer for chat**
11. **Implement options selector UI component**
12. **Add canvas action auto-apply mechanism**

