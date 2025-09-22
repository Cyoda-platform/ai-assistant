
# Cyoda Python Client Application Development Guide

This guide helps you build **Cyoda Python client applications** using the established patterns in this codebase. **Always reference `example_application/` for working examples** - don't reinvent the wheel.

## Core Principles
- **Interface-based design** - Extend CyodaEntity/CyodaProcessor base classes
- **Workflow-driven architecture** - All business logic flows through Cyoda workflows
- **Thin routes** - Pure proxies to EntityService with no business logic
- **Manual transitions only** - Entity updates must specify manual transitions explicitly

## Critical Rules
- **NEVER modify** `common/` directory - framework code only
- **ALWAYS validate workflows** against `example_application/resources/workflow/workflow_schema.json`
- **ALWAYS review requirements** in `application/resources/functional_requirements/`
- **ALWAYS run code quality checks**: `mypy`, `black`, `isort`, `flake8`, `bandit`
- **Use entity constants** (ENTITY_NAME/ENTITY_VERSION) instead of hardcoded strings
- **Follow example_application/ patterns exactly**

## Implementation Workflow

### 1. Prerequisites & Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Study Requirements & Reference Implementation
**FIRST - Review functional requirements:**
- **Requirements**: `application/resources/functional_requirements/` - Contains all business requirements for your application

**Then examine reference patterns in `example_application/`:**
- **Entity**: `entity/example_entity.py` - Shows CyodaEntity extension patterns
- **Processor**: `processor/example_entity_processor.py` - Business logic implementation
- **Criterion**: `criterion/example_entity_validation_criterion.py` - Validation logic
- **Workflow**: `resources/workflow/example_entity/version_1/ExampleEntity.json` - Workflow structure - must validate against `example_application/resources/workflow/workflow_schema.json`
- **Routes**: See `application/routes/` for API endpoint patterns

### 3. Create Your Entities for your application
**Location**: `application/entity/{entity_name}/version_1/{entity_name}.py`
- Extend `CyodaEntity` from `common.entity.cyoda_entity`
- Define `ENTITY_NAME` and `ENTITY_VERSION` constants
- Add business fields with Pydantic Field definitions
- **Reference**: `example_application/entity/example_entity.py`

### 4. Define Workflows: 1 workflow per entity
**Location**: `application/resources/workflow/{entity_name}/version_1/{EntityName}.json`
- Copy structure from `example_application/resources/workflow/example_entity/version_1/ExampleEntity.json`
- Use `"initial_state"` as initial state
- Set explicit `"manual": true/false` for all transitions
- Match processor names to your Python class names exactly
- **CRITICAL**: Validate against `example_application/resources/workflow/workflow_schema.json`
- **Reference**: `example_application/resources/workflow/example_entity/version_1/ExampleEntity.json`

### 5. Implement Processors
**Location**: `application/processor/{entity_name}_processor.py`
- Extend `CyodaProcessor` from `common.processor.base`
- Use `cast_entity()` for type-safe entity operations
- Access other entities via `get_entity_service()`
- **Reference**: `example_application/processor/example_entity_processor.py`

### 6. Create API Routes
**Location**: `application/routes/{entity_name}s.py`
- Create Quart Blueprint with `/api/{entity}` prefix
- Use `get_entity_service()` for all CRUD operations
- Return technical IDs and entity states
- **Reference**: `application/routes/pets.py` or other route files

### 7. Register Components
**Update `services/config.py`:**
- Add your processor/criterion modules to the `modules` list
- **Reference**: See existing module registration pattern

**Update `application/app.py`:**
- Register your route blueprints
- **Reference**: `application/app.py` for blueprint registration pattern

## Key Patterns & Best Practices

### Entity Patterns
- Use business IDs for entity references, never technical UUIDs in data
- Cast entities with `cast_entity()` for type safety
- Define ENTITY_NAME/ENTITY_VERSION constants

### Processor Patterns
- Access other entities via `get_entity_service()`
- Use async/await for all operations
- Log business operations appropriately

### Route Patterns
- Thin proxies to EntityService only
- Return technical IDs in responses
- Use entity constants, not hardcoded strings

### Testing & Quality
- Run: `mypy`, `black`, `isort`, `flake8`, `bandit`

## Development Environment

### Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### Code Quality
```bash
black . && isort . && mypy . && flake8 . && bandit -r . -x tests/
```

## Workflow Management

### Workflow Validation (CRITICAL!)
Before importing, validate your workflow files:
- **Schema**: `example_application/resources/workflow/workflow_schema.json`
- Ensure your workflow JSON matches the required schema structure
- Validate processor names match your Python class names exactly

## Completion Checklist
- [ ] **Requirements reviewed** from `application/resources/functional_requirements/`
- [ ] All entities extend CyodaEntity with ENTITY_NAME/ENTITY_VERSION constants
- [ ] All workflows validated against `example_application/resources/workflow/workflow_schema.json`
- [ ] All workflows use "initial_state" with explicit manual flags
- [ ] All processors extend CyodaProcessor and log execution
- [ ] All routes are thin proxies to EntityService
- [ ] Code quality checks pass: `mypy`, `black`, `isort`, `flake8`, `bandit`
- [ ] No modifications to `common/` directory

## Success Criteria
1. **Code Quality** - All quality checks pass
2. **Requirements Coverage** - All functional requirements implemented
3. **Workflow Compliance** - Proper initial state and transition rules
4. **Architecture Adherence** - Follow established patterns in `example_application/`
