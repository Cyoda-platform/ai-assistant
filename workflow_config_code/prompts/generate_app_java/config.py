"""
GenerateCriteriaE5f4PromptConfig Configuration

Configuration data for the generate processors and criteria prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
# Cyoda Client Application Development Guide

This project is a **Cyoda client application** built with Spring Boot and Gradle for building scalable web clients with workflow-driven backend interactions.

## Core Principles
- **Interface-based design** - No Java reflection, use CyodaEntity/CyodaProcessor interfaces
- **Workflow-driven architecture** - All business logic flows through Cyoda workflows
- **Thin controllers** - Pure proxies to EntityService with no business logic
- **Manual transitions only** - Entity updates must specify manual transitions explicitly
- **Technical ID performance** - Use UUIDs in API responses for optimal performance

## Critical Rules
- **NEVER modify** `src/main/java/com/java_template/common/` directory
- **ALWAYS compile** after each component: `./gradlew clean compileJava`
- **Processors are read-only** for current entity; can CRUD other entities via EntityService
- **Import QueryCondition** for search conditions: `List<QueryCondition>` not `List<SimpleCondition>`
- **Use Config.ENTITY_VERSION** constant (1) instead of hardcoded versions

## Project Structure
```
src/main/java/com/java_template/
├── Application.java                    # Main Spring Boot application
├── common/                            # Framework code - DO NOT MODIFY
└── application/                       # Your business logic - CREATE AS NEEDED
    ├── controller/                    # REST endpoints (/ui/**)
    ├── entity/{name}/version_1/       # Domain entities implementing CyodaEntity
    ├── processor/                     # Workflow processors implementing CyodaProcessor
    └── criterion/                     # Workflow criteria implementing CyodaCriterion
```

## Implementation Workflow

### 1. Prerequisites & Planning
```bash
./gradlew build  # Ensure generated classes exist
```
- Review `src/main/resources/functional_requirements/*` to understand requirements. There can be multiple files - study them all.
- Study examples in `llm_example/code/application/` directory
- Plan entities and their relationships

### 2. Entity Implementation
**Location**: `application/entity/{entity_name}/version_1/{EntityName}.java`

**Template**:
```java
@Data
public class EntityName implements CyodaEntity {
    public static final String ENTITY_NAME = EntityName.class.getSimpleName();
    public static final Integer ENTITY_VERSION = 1;
    
    // Business ID field (required)
    private String entityId;
    
    // Required fields per requirements
    // Optional fields
    // Nested classes for complex structures
    
    @Override
    public OperationSpecification getModelKey() {
        ModelSpec modelSpec = new ModelSpec();
        modelSpec.setName(ENTITY_NAME);
        modelSpec.setVersion(ENTITY_VERSION);
        return new OperationSpecification.Entity(modelSpec, ENTITY_NAME);
    }
    
    @Override
    public boolean isValid() {
        return entityId != null && !entityId.trim().isEmpty();
        // Add other required field validations
    }
}
```

### 3. Workflow Definition
**Location**: `src/main/resources/workflow/{entityName}/version_1/{EntityName}.json`

**Key Requirements**:
- Use `"initial"` as initial state (not `"none"` - reserved keyword)
- All transitions must have explicit `"manual": true/false` flags
- Processor names must match Spring component class names exactly
- Keep simple unless requirements demand complexity

**Template**:
```json
{
  "version": "1.0",
  "name": "EntityName",
  "desc": "Entity lifecycle workflow",
  "initialState": "initial",
  "active": true,
  "states": {
    "initial": {
      "transitions": [
        {
          "name": "create_entity",
          "next": "active",
          "manual": false
        }
      ]
    },
    "active": {
      "transitions": [
        {
          "name": "update_entity",
          "next": "active",
          "manual": true,
          "processors": [
            {
              "name": "ProcessorName",
              "executionMode": "ASYNC_NEW_TX",
              "config": {
                "attachEntity": true,
                "calculationNodesTags": "cyoda_application",
                "responseTimeoutMs": 3000,
                "retryPolicy": "FIXED"
              }
            }
          ]
        }
      ]
    }
  }
}
```

### 4. Processor Implementation
**Location**: `application/processor/{ProcessorName}.java`

**Template**:
```java
@Component
public class ProcessorName implements CyodaProcessor {
    private static final Logger logger = LoggerFactory.getLogger(ProcessorName.class);
    private final String className = this.getClass().getSimpleName();
    private final ProcessorSerializer serializer;
    private final EntityService entityService; // Only if needed for other entities

    public ProcessorName(SerializerFactory serializerFactory, EntityService entityService) {
        this.serializer = serializerFactory.getDefaultProcessorSerializer();
        this.entityService = entityService;
    }

    @Override
    public EntityProcessorCalculationResponse process(CyodaEventContext<EntityProcessorCalculationRequest> context) {
        EntityProcessorCalculationRequest request = context.getEvent();
        logger.info("Processing {} for request: {}", className, request.getId());

        return serializer.withRequest(request)
                .toEntityWithMetadata(EntityClass.class)
                .validate(this::isValidEntityWithMetadata, "Invalid entity wrapper")
                .map(this::processBusinessLogic)
                .complete();
    }

    @Override
    public boolean supports(OperationSpecification modelSpec) {
        return className.equalsIgnoreCase(modelSpec.operationName());
    }
    
    // Implementation methods...
}
```

### 5. Controller Implementation
**Location**: `application/controller/{EntityName}Controller.java`

**Key Patterns**:
- Map to `/ui/{entity}/**` endpoints
- Accept entities as `@RequestBody`, not Map objects
- Return `EntityWithMetadata<T>` or technical IDs
- Use `entityService.findByBusinessId()` for business ID lookups
- Import `QueryCondition` for search conditions

**Search Condition Template**:
```java
// Build search conditions
List<QueryCondition> conditions = new ArrayList<>();

SimpleCondition condition = new SimpleCondition()
        .withJsonPath("$.fieldName")
        .withOperation(Operation.EQUALS)
        .withValue(objectMapper.valueToTree(value));
conditions.add(condition);

GroupCondition groupCondition = new GroupCondition()
        .withOperator(GroupCondition.Operator.AND)
        .withConditions(conditions);

List<EntityWithMetadata<Entity>> results = entityService.search(modelSpec, groupCondition, Entity.class);
```

## Common Patterns & Best Practices

### Entity Relationships
- Use business IDs for entity references in data structures
- Use EntityService to fetch related entities in processors
- Never store technical UUIDs in entity data

### Error Handling
- Validate entities in processors with `isValid()`
- Log all business operations with appropriate levels
- Return proper HTTP status codes in controllers

### Performance Optimization
- Use `findByBusinessId()` for single entity lookups
- Use `search()` with conditions for filtered queries
- Return slim DTOs for list endpoints, full entities for detail endpoints

### Testing Strategy
- Compile frequently: `./gradlew clean compileJava`
- Use exact entity names from ENTITY_NAME constants for workflow imports

## Completion Checklist
- [ ] All entities implement CyodaEntity with proper validation
- [ ] All workflows use "initial" state (not "none") with explicit manual flags
- [ ] All controllers are thin proxies with no business logic
- [ ] Project compiles successfully: `./gradlew build`
- [ ] All functional requirements satisfied
- [ ] No modifications to `common/` directory
- [ ] Summary documentation added to root directory of the project with the description of the application (what you built, how to validate it works, etc.)

## Success Criteria
The implementation is complete when:
1. **Full compilation** - `./gradlew build` succeeds
2. **Requirements coverage** - All user requirements implemented
3. **Workflow compliance** - All transitions follow manual/automatic rules with proper initial state
4. **Architecture adherence** - No reflection, thin controllers, proper separation
"""
