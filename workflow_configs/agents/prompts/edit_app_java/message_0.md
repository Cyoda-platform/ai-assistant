# Cyoda Client Application Editing Guide

This project is a **Cyoda client application** built with Spring Boot and Gradle. You are working on **editing an EXISTING application**, not building from scratch.

## Core Principles
- **Interface-based design** - No Java reflection, use CyodaEntity/CyodaProcessor interfaces
- **Workflow-driven architecture** - All business logic flows through Cyoda workflows
- **Thin controllers** - Pure proxies to EntityService with no business logic
- **Manual transitions only** - Entity updates must specify manual transitions explicitly
- **Technical ID performance** - Use UUIDs in API responses for optimal performance

## Golden Rules

- No reflection.
- Do not modify anything in src/main/java/com/java_template/common.
- Compile early and often; fix errors immediately.
- Controllers = thin proxies to EntityService (no business logic).
- Prefer technical IDs for performance.
- In processors, you cannot update the current entity (read-only); you may get/update/delete other entities via EntityService.
- **CRITICAL: Update using only manual transitions (never automatic).**

## IDs & Metadata

- **Technical ID (UUID, unique, immutable)**:
  `entityResponse.getMetadata().getId()`
- **Entity state**:
  `entityResponse.getMetadata().getState()`
  Entity state is managed by the workflow and you can not change it manually, you can only read it.
 If requirements mention "state" or "status", map them to `entity.meta.state` instead and explain this to the user.

- **Business ID (user-defined, non-unique, mutable)**:
  retrievable/updatable with business ID–specific methods.
- **Update semantics**:
  - With transition → moves to that state.
  - Without transition → loops back to same state.
  - If in doubt, save without transition.

## Critical Rules
- **NEVER modify** `src/main/java/com/java_template/common/` directory
- **ALWAYS compile** after each change: `./gradlew clean compileJava`
- **Processors are read-only** for current entity; can CRUD other entities via EntityService
- **Import QueryCondition** for search conditions: `List<QueryCondition>` not `List<SimpleCondition>`
- **Use Config.ENTITY_VERSION** constant (1) instead of hardcoded versions

## Project Structure
```
src/main/java/com/java_template/
├── Application.java                    # Main Spring Boot application
├── common/                            # Framework code - DO NOT MODIFY
└── application/                       # Your business logic - EDIT AS NEEDED
    ├── controller/                    # REST endpoints (/ui/**)
    ├── entity/{name}/version_1/       # Domain entities implementing CyodaEntity
    ├── processor/                     # Workflow processors implementing CyodaProcessor
    └── criterion/                     # Workflow criteria implementing CyodaCriterion
```

## EDITING Workflow - CRITICAL DIFFERENCES FROM BUILD

### 1. Prerequisites & Understanding Current State

**CRITICAL: You are EDITING, not building from scratch. Follow this process:**

```bash
./gradlew build  # Ensure generated classes exist and app compiles
```

**Step 1: Scan for Requirements**
Look in `src/main/resources/functional_requirements/` for these files:
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
- Study the current implementation in `src/main/java/com/java_template/application/`
- Review existing entities, processors, criteria, and controllers
- Understand current workflow definitions in `src/main/resources/workflow/`
- **DO NOT start from scratch - build on what exists**

**Step 4: Study Examples (if needed)**
- Check `llm_example/code/application/` for patterns and best practices
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
   - common/service/EntityService.java
   - common/workflow/CyodaEntity.java
   - common/workflow/CyodaEventContext.java
2. **Examples**: llm_example/code/application (processors, criteria, controllers)
   **Use examples only for NEW components you need to add.**

3. **Functional Requirements**
   - **PRIMARY**: src/main/resources/functional_requirements/editing_requirement.md
   - **CONTEXT**: src/main/resources/functional_requirements/combined_requirements.md
   - **HISTORICAL**: src/main/resources/functional_requirements/user_requirement.md
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
- [ ] Compile after each significant change: `./gradlew clean compileJava`
- [ ] Test that existing functionality still works

### After Editing
- [ ] Final compilation: `./gradlew clean build`
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
3. Update controllers if API changes
4. Recompile and test

### Scenario 2: Add New Workflow Transition
1. Update workflow JSON in `src/main/resources/workflow/`
2. Implement new processor if needed
3. Update any criteria if needed
4. Recompile and test

### Scenario 3: Add New Endpoint
1. Create or update controller in `application/controller/`
2. Ensure it uses EntityService correctly
3. Test endpoint functionality

### Scenario 4: Modify Business Logic
1. Update relevant processor in `application/processor/`
2. Ensure read-only constraint for current entity
3. Recompile and test workflow

## CRITICAL REMINDERS FOR EDITING

1. **READ editing_requirement.md FIRST** - this is your primary task definition
2. **DON'T recreate what exists** - modify existing code
3. **Compile frequently** - catch errors early
4. **Test existing features** - ensure no breaking changes
5. **Keep changes minimal** - only what's needed for the requirement

## Error Recovery
- Compilation errors? Fix immediately before proceeding
- Missing classes? Check if `./gradlew build` generated them
- EntityService errors? Review common/service/EntityService.java
- Workflow errors? Verify JSON syntax and processor implementations

## Final Notes
You are editing an existing, working application. Your goal is to make targeted improvements based on editing_requirement.md while maintaining the stability and functionality of the existing codebase. Think "surgical changes" not "rebuild from scratch."
