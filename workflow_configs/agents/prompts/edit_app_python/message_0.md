# Cyoda Python Client Application Editing Guide

This project is a **Cyoda Python client application**. You are working on **editing an EXISTING application**, not building from scratch.

## Core Principles
- **Interface-based design** - Extend CyodaEntity/CyodaProcessor base classes
- **Workflow-driven architecture** - All business logic flows through Cyoda workflows
- **Thin routes** - Pure proxies to EntityService with no business logic
- **Manual transitions only** - Entity updates must specify manual transitions explicitly

## Golden Rules

- Modify only the application directory.
- Statically check with `mypy .` early and often; fix errors immediately.
- Routes = thin proxies to EntityService (no business logic).
- Prefer technical IDs for performance.
- In processors, you cannot use entityService to update the current entity (read-only); The current entity will be updated automatically once you return from the processor.
  you may get/update/delete other entities via EntityService.
- **CRITICAL: Update using only manual transitions (never automatic).**

## IDs & Metadata

- **Technical ID (UUID, unique, immutable)**:
  `entity.id` - retrievable from CyodaEntity
- **Entity state**:
  `entity.state` - Entity state is managed by the workflow and you can not change it manually, you can only read it.
 If requirements mention "state" or "status", map them to `entity.meta.state` instead and explain this to the user.

- **Business ID (user-defined, non-unique, mutable)**:
  retrievable/updatable with business ID–specific methods.
- **Update semantics**:
  - With transition → moves to that state.
  - Without transition → loops back to same state.
  - If in doubt, save without transition.

## Critical Rules
- **NEVER modify** `common/` directory - framework code only
- **ALWAYS validate workflows** against `example_application/resources/workflow/workflow_schema.json`
- **ALWAYS run code quality checks**: `mypy`, `black`, `isort`, `flake8`, `bandit`
- **Use entity constants** (ENTITY_NAME/ENTITY_VERSION) instead of hardcoded strings

## Project Structure
```
application/
├── entity/{entity_name}/version_1/  # Domain entities extending CyodaEntity
├── processor/                       # Workflow processors extending CyodaProcessor
├── criterion/                       # Workflow criteria extending CyodaCriterion
├── routes/                          # API endpoints
└── resources/
    ├── functional_requirements/     # Business requirements
    └── workflow/{entity_name}/version_1/  # Workflow JSONs
```

## EDITING Workflow - CRITICAL DIFFERENCES FROM BUILD

### 1. Prerequisites & Understanding Current State

**CRITICAL: You are EDITING, not building from scratch. Follow this process:**

```bash
mypy .  # Ensure code passes type checking
```

**Step 1: Scan for Requirements**
Look in `application/resources/functional_requirements/` for these files:
- **editing_requirement.md** - THE CURRENT EDITING REQUEST (PRIMARY SOURCE)
- **combined_requirements.md** - Original + editing requirements combined (CONTEXT)
- **user_requirement.md** - Original application requirements (HISTORICAL CONTEXT)
- Any uploaded files from the user

**Step 2: Understand What to Edit**
- Read **editing_requirement.md** first - this tells you what changes to make
- Read **combined_requirements.md** for full context
- Understand the original intent from **user_requirement.md**
- Review any uploaded files for additional context

**Step 3: Analyze Existing Code**
- Study the current implementation in `application/`
- Review existing entities, processors, criteria, and routes
- Understand current workflow definitions in `application/resources/workflow/`
- **DO NOT start from scratch - build on what exists**

**Step 4: Study Examples (if needed)**
- Check `example_application/` for patterns and best practices
- Only reference examples for NEW components you need to add

### 2. Planning Your Edits

Based on **editing_requirement.md**, determine:
1. Which existing files need modification?
2. Which new files need to be created?
3. Which workflows need updating?
4. Do any entity definitions need changes?

**IMPORTANT: Minimize changes. Only modify what's necessary for the editing requirement.**

## Repository Map

1. **Core APIs & Types**
   - common/service/entity_service.py
   - common/entity/cyoda_entity.py
   - common/processor/base.py
2. **Examples**: example_application/ (processors, criteria, routes)
   **Use examples only for NEW components you need to add.**

3. **Functional Requirements**
   - **PRIMARY**: application/resources/functional_requirements/editing_requirement.md
   - **CONTEXT**: application/resources/functional_requirements/combined_requirements.md
   - **HISTORICAL**: application/resources/functional_requirements/user_requirement.md
   - **Additional files** uploaded by user

## Implementation Checklist for EDITING

### Before Starting
- [ ] Read editing_requirement.md thoroughly
- [ ] Understand what changes are requested
- [ ] Review combined_requirements.md for full context
- [ ] Analyze existing code structure
- [ ] Plan minimal changes needed

### During Editing
- [ ] Modify existing files rather than recreating them
- [ ] Add new components only if required by editing_requirement.md
- [ ] Update workflow JSONs if states/transitions change
- [ ] Run type checking after each significant change: `mypy .`
- [ ] Test that existing functionality still works

### After Editing
- [ ] Final type checking: `mypy .`
- [ ] Run code quality checks: `black .`, `isort .`, `flake8 .`, `bandit -r .`
- [ ] Verify all requirements from editing_requirement.md are met
- [ ] Ensure no breaking changes to existing functionality
- [ ] Test the edited features

## Key Differences: Build vs Edit

| Aspect | Build (New App) | Edit (Existing App) |
|--------|----------------|-------------------|
| **Primary Source** | user_requirement.md | editing_requirement.md |
| **Approach** | Create from scratch | Modify existing code |
| **Code Review** | Study examples | Study existing implementation |
| **Changes** | Create all components | Minimal necessary changes |
| **Testing** | New functionality | New + existing functionality |

## Common Editing Scenarios

### Scenario 1: Add New Field to Entity
1. Update entity class in `application/entity/{name}/version_1/`
2. Update any affected processors
3. Update routes if API changes
4. Run `mypy .` and test

### Scenario 2: Add New Workflow Transition
1. Update workflow JSON in `application/resources/workflow/`
2. Implement new processor if needed
3. Update any criteria if needed
4. Validate against schema and test

### Scenario 3: Add New Endpoint
1. Create or update route in `application/routes/`
2. Ensure it uses EntityService correctly
3. Test endpoint functionality

### Scenario 4: Modify Business Logic
1. Update relevant processor in `application/processor/`
2. Ensure read-only constraint for current entity
3. Run `mypy .` and test workflow

## CRITICAL REMINDERS FOR EDITING

1. **READ editing_requirement.md FIRST** - this is your primary task definition
2. **DON'T recreate what exists** - modify existing code
3. **Run type checks frequently** - catch errors early with `mypy .`
4. **Test existing features** - ensure no breaking changes
5. **Keep changes minimal** - only what's needed for the requirement

## Error Recovery
- Type errors? Fix immediately before proceeding with `mypy .`
- Missing classes? Check if entity files exist and are properly imported
- EntityService errors? Review common/service/entity_service.py
- Workflow errors? Verify JSON syntax and validate against schema

## Final Notes
You are editing an existing, working application. Your goal is to make targeted improvements based on editing_requirement.md while maintaining the stability and functionality of the existing codebase. Think "surgical changes" not "rebuild from scratch."
