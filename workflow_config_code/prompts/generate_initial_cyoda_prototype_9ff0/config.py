"""
GenerateInitialCyodaPrototype9ff0PromptConfig Configuration

Generated from config: workflow_configs/prompts/generate_initial_cyoda_prototype_9ff0/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """You are provided with a Java codebase that implements a REST API (using Spring Boot framework).
Currently, the code uses local in‑memory dictionaries (and counters) to store and manage data for one or more entity types.
Your task is to refactor the code so that all interactions with the local cache are replaced by calls to an external service called com.java_template.common.service.EntityService. Note, that EntityService is a bean, so inject it with Controller constructor.
You can use only these functions for replacement - if this is not enough just skip and leave as is
You can use a constant for EntityName: each EntityName class has a public constant ENTITY_NAME
1. CompletableFuture<UUID> idFuture = entityService.addItem(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION,  # always use this constant
    entity=data  # the validated data object
)
Note: entityService.addItem returns technicalId of the created entity.
CompletableFuture<List<UUID>> addItems idsFuture = entityService.addItems(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION,  # always use this constant
    entities=data
)
Note: entityService.addItems returns a list of technicalIds of the created entities.
2. Data retrieval. You can use the following methods:
 Use getItem to retrieve a single entity by technicalId.
CompletableFuture<ObjectNode> itemFuture = entityService.getItem(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION,
    technicalId=<technicalId>
)-- ObjectNode node will have entity data and technicalId field
Get all: 
CompletableFuture<ArrayNode> itemsFuture = entityService.getItems(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION,
) -- each node will have technicalId field added automatically
Get items by field that is not technicalId: 
CompletableFuture<ArrayNode> filteredItemsFuture = entityService.getItemsByCondition(
    entityModel={EntityName}.ENTITY_NAME,
    entityVersion=ENTITY_VERSION,
    condition=condition,
    inMemory=true
)
 inMemory=true means that the search will be performed in memory, not in the database. It is useful for optimization purposes.
Please use the following classes to construct search conditions for entity queries:
Condition (com.java_template.common.util.Condition) and SearchConditionRequest (com.java_template.common.util.SearchConditionRequest)

To create a single condition, wrap it into a SearchConditionRequest with one element in the list:
com.java_template.common.util.SearchConditionRequest.group("AND",
    com.java_template.common.util.Condition.of("$.field", "EQUALS", "value")
)
To create a group of multiple conditions with logical operator AND or OR, use:
com.java_template.common.util.SearchConditionRequest.group("OR",
    com.java_template.common.util.Condition.of("$.field1", "EQUALS", "value1"),
    com.java_template.common.util.Condition.of("$.field2", "GREATER_THAN", 10)
)
Supported operatorType values (for Condition):
"EQUALS", "NOT_EQUAL", "IEQUALS", "INOT_EQUAL", "IS_NULL", "NOT_NULL",
"GREATER_THAN", "GREATER_OR_EQUAL", "LESS_THAN", "LESS_OR_EQUAL",
"ICONTAINS", "ISTARTS_WITH", "IENDS_WITH", "INOT_CONTAINS",
"INOT_STARTS_WITH", "INOT_ENDS_WITH", "MATCHES_PATTERN",
"BETWEEN", "BETWEEN_INCLUSIVE"

Note: If the operatorType starts with the letter 'I', it means the comparison should ignore case (e.g., "IEQUALS" = equals ignoring case).
Supported operator values (for SearchConditionRequest): "AND", "OR"
Pass the resulting SearchConditionRequest as the third argument (condition) to:
entityService.getItemsByCondition(entityModel, entityVersion, condition, inMemory)
Avoid any update operations. You can add todo instead of actual update.
use 'import static com.java_template.common.config.Config.*;' to import ENTITY_VERSION
import com.java_template.common.service.EntityService
use package com.java_template.application.controller; and class name 'Controller'
Lombok is already configured in the project via io.freefair.lombok plugin. Please use Lombok annotations like @Data, @Getter, @Setter, @AllArgsConstructor, @NoArgsConstructor, etc., instead of manually writing getters, setters, and constructors, and make sure to include the necessary Lombok imports in the generated code.
Assign a unique @RequestMapping path to each controller to avoid conflicts.

Preserve the endpoint routes and any other essential business logic like data ingestion, calling any external apis, mocks, calculations etc.
Please use correct logging, e.g. org.slf4j.Logger logger = org.slf4j.LoggerFactory.getLogger(Controller.class);
Response format: respond with only the code. No markdown formatting, no explanation. Regular Java comments (// like this) are allowed, but avoid extra narrative or markdown-style formatting. Do not include code block markers like ```.
** Keep all the endpoints in a single class Controller (like in the prototype) - do not add multiple controller classes - just a single one. **
Wrap endpoints with try-catch and handle exceptions. Return HTTP 400 for IllegalArgumentException, 500 for all others.
Exhaustive list of EntityService methods:
CompletableFuture<UUID> addItem(String entityModel, String entityVersion, Object entity);
CompletableFuture<List<UUID>> addItems(String entityModel, String entityVersion, Object entities);
CompletableFuture<ObjectNode> getItem(String entityModel, String entityVersion, UUID technicalId);
CompletableFuture<ArrayNode> getItems(String entityModel, String entityVersion);
CompletableFuture<ArrayNode> getItemsByCondition(String entityModel, String entityVersion, Object condition, boolean inMemory);
CompletableFuture<UUID> deleteItem(String entityModel, String entityVersion, UUID technicalId);
EntityService doesn't have any other methods, please do not reinvent anything else."""
