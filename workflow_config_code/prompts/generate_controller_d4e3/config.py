"""
GenerateControllerD4e3PromptConfig Configuration

Configuration data for the generate controller prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """You are tasked with generating an event-driven REST API controller based on functional requirements.

IMPORTANT: The controller should be "dull" - it only handles entity persistence and triggers workflows. ALL business logic from the functional requirements will be implemented in workflows, NOT in the controller.

### 1. DISCOVERY PHASE (MANDATORY)
**You must use the following tools:**
- Use `list_directory_files` to discover all entity classes in 'src/main/java/com/java_template/application/entity'
- Use `read_file` to examine each entity class and understand their fields and structure

Optional:
- Use `list_directory_files` to discover all workflow files in 'src/main/java/com/java_template/application/workflow'

### 2. ANALYSIS PHASE
1. Analyze the functional requirements to identify API endpoints needed
2. Identify the main entities from the discovered entity classes
3. Understand entity structure and fields from the entity class files
4. Plan event-driven endpoints following the EDA pattern

**Event-Driven Flow Pattern (EDA-Compliant):**
1. **POST /entityName** → Create entity → Save to cache → Trigger `processEntityName(entity)` → Return response
   - If you have an orchestration entity (like Job, Task, Workflow), it should have a POST endpoint to create it, and a GET by technicalId to retrieve it. You will most likely not need any other POST endpoints for business entities as saving business entity is done via the process method.
2. **GET /entityName/{id}** → Retrieve from cache → Return entity. Each entity should have a GET by technicalId.
3. Only if the user explicitly asked for update: **POST /entityName/{id}/update** → Create new entity version → Save to cache → Trigger `processEntityName(entity)` → Return response (still avoid unless necessary)
4. Only if the user explicitly asked for delete/deactivate: **POST /entityName/{id}/deactivate** → Create deactivation record → Save to cache → Return confirmation (still avoid unless necessary)

CONTROLLER RESPONSIBILITIES (ONLY):
- Accept HTTP requests
- Validate basic request format
- Save entities using EntityService
- Retrieve entities using EntityService
- Return appropriate HTTP responses
- Handle exceptions

DO NOT IMPLEMENT:
- Business rules or logic
- Complex validations
- Calculations or transformations
- External API calls
- Workflow orchestration
- Data processing beyond basic entity persistence

ENTITY USAGE:
- Import and reuse existing entity classes from 'src/main/java/com/java_template/application/entity'
- DO NOT create static classes for entities
- Static classes are allowed ONLY for request/response DTOs
- Entity classes must be reused as-is

EntityService Operations Available:
1. ADD:
CompletableFuture<UUID> idFuture = entityService.addItem(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION,
    entity=data
)

CompletableFuture<List<UUID>> idsFuture = entityService.addItems(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION,
    entities=data
)

2. READ:
CompletableFuture<ObjectNode> itemFuture = entityService.getItem(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION,
    technicalId=technicalId
)

CompletableFuture<ArrayNode> itemsFuture = entityService.getItems(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION
)

CompletableFuture<ArrayNode> filteredItemsFuture = entityService.getItemsByCondition(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION,
    condition=condition,
    inMemory=true
)

3. DELETE:
CompletableFuture<UUID> deletedId = entityService.deleteItem(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION,
    technicalId=technicalId
)

Search Conditions (for simple filtering only):
Use SearchConditionRequest.group() and Condition.of() for basic field-based queries:
SearchConditionRequest.group("AND",
    Condition.of("$.fieldName", "EQUALS", "value")
)

Supported operators: "EQUALS", "NOT_EQUAL", "IEQUALS", "GREATER_THAN", "LESS_THAN", etc.

Required Imports and Configuration:
- import static com.java_template.common.config.Config.*;
- import com.java_template.common.service.EntityService;
- package com.java_template.application.controller;
- class name: Controller
- Use Lombok annotations (@Data, @Getter, @Setter, etc.)
- Use SLF4J logging: Logger logger = LoggerFactory.getLogger(Controller.class);
- Inject EntityService via constructor
- Use unique @RequestMapping path

Exception Handling:
- Wrap endpoints in try-catch
- Return HTTP 400 for IllegalArgumentException
- Return HTTP 500 for all other exceptions

Response Format:
- Respond with only the Java code
- No markdown formatting or explanations
- Use regular Java comments only
- Single Controller class with all endpoints

Remember:
- Start with the DISCOVERY PHASE using the tools
- Follow the Event-Driven Flow Pattern
- Keep the controller simple and "dull" - all business intelligence goes in workflows!
- Reuse existing entity classes, don't recreate them

Return java code only. No markdown formatting or explanations. The code should be ready to be pasted into the file.
"""
