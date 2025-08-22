"""
GenerateControllerD4e3PromptConfig Configuration

Configuration data for the generate controller prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
You are Java 21 Spring Boot 3 developer. You are tasked with generating an event-driven REST API controller for {split_parameter_value} entity only,  based on functional requirements. 
The controller must be dull – it is just a proxy to the entity service for {split_parameter_value} entity. And only this entity.
All business logic from the functional requirements will be implemented in workflows, not in the controller. So just proxy the requests to the entity service.

2. ANALYSIS PHASE
3. Analyze the functional requirements to identify API endpoints needed
5. Understand entity structure and fields from the entity class files

Controller Responsibilities:

* Accept HTTP requests
* Validate basic request format
* Save entities using EntityService
* Retrieve entities using EntityService
* Return appropriate HTTP responses
* Handle exceptions with ExecutionException unwrapping for cause inspection

Do Not Implement any business logic in the controller.

Entity Usage:

* Import and reuse existing entity classes from their correct versioned packages under 'src/main/java/com/java_template/application/entity'
* Do not create static classes for entities
* Add static classes only for request/response DTOs that represent request/response payloads from the functional requirements
* Request/Response DTOs must be created as static classes within the controller and must match the request/response payloads from the functional requirements
* Request/Response DTOs must be created with io.swagger.v3.oas.annotations.media.Schema annotations
* Entity classes must be reused as-is

EntityService Operations Available:
1. ADD:
   CompletableFuture<UUID> idFuture = entityService.addItem(
   entityModel={split_parameter_value}.ENTITY_NAME,
   entityVersion=String.valueOf({split_parameter_value}.ENTITY_VERSION),
   entity=data
   )

CompletableFuture<List<UUID>> idsFuture = entityService.addItems(
entityModel={split_parameter_value}.ENTITY_NAME,
entityVersion=String.valueOf({split_parameter_value}.ENTITY_VERSION),
entities=data
)

2. READ:
   CompletableFuture<ObjectNode> itemFuture = entityService.getItem(
   entityModel={split_parameter_value}.ENTITY_NAME,
   entityVersion=String.valueOf({split_parameter_value}.ENTITY_VERSION),
   technicalId=UUID.fromString(technicalId)
   )

CompletableFuture<ArrayNode> itemsFuture = entityService.getItems(
entityModel={split_parameter_value}.ENTITY_NAME,
entityVersion=String.valueOf({split_parameter_value}.ENTITY_VERSION)
)

CompletableFuture<ArrayNode> filteredItemsFuture = entityService.getItemsByCondition(
entityModel={split_parameter_value}.ENTITY_NAME,
entityVersion=String.valueOf({split_parameter_value}.ENTITY_VERSION),
condition=condition,
inMemory=true
)

3. UPDATE:
   CompletableFuture<UUID> updatedId = entityService.updateItem(
   entityModel={split_parameter_value}.ENTITY_NAME,
   entityVersion=String.valueOf({split_parameter_value}.ENTITY_VERSION),
   technicalId=UUID.fromString(technicalId),
   entity=data
   )

4. DELETE:
   CompletableFuture<UUID> deletedId = entityService.deleteItem(
   entityModel={split_parameter_value}.ENTITY_NAME,
   entityVersion=String.valueOf({split_parameter_value}.ENTITY_VERSION),
   technicalId=UUID.fromString(technicalId)
   )

Search Conditions (for simple filtering only):
Use SearchConditionRequest.group() and Condition.of() for basic field-based queries:
SearchConditionRequest.group("AND",
Condition.of("$.fieldName", "EQUALS", "value")
)

Supported operators: "EQUALS", "NOT_EQUAL", "IEQUALS", "GREATER_THAN", "LESS_THAN", etc.

Required Imports and Configuration:
* import static com.java_template.common.config.Config.*;
* import com.java_template.common.service.EntityService;
* import com.java_template.common.util.Condition; //if needed
* import com.java_template.common.util.SearchConditionRequest;//if needed
* package com.java_template.application.controller.{split_parameter_value_lower}.version_1;
* class name: {split_parameter_value}Controller
* Use Lombok annotations (@Data, @Getter, @Setter, etc.)
* Use SLF4J logging: Logger logger = LoggerFactory.getLogger({split_parameter_value}Controller.class);
* Inject EntityService via constructor
* Use unique @RequestMapping path
* Always convert technicalId from request path to UUID using UUID.fromString()

Exception Handling:
* Wrap endpoints in try-catch
* Return HTTP 400 for IllegalArgumentException
* For ExecutionException, unwrap the cause: if NoSuchElementException, return HTTP 404; if IllegalArgumentException, return HTTP 400; otherwise return HTTP 500
* Return HTTP 500 for all other exceptions

Swagger Documentation:
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.media.ArraySchema;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

* Add Swagger annotations for API documentation
* Include @Operation(summary = "Summary", description = "Description") for each endpoint
* Include @Parameter(name = "technicalId", description = "Technical ID of the entity") for path parameters
* Include @RequestBody for request payloads
* Include @ApiResponse(responseCode = "200", description = "OK", content = @Content(schema = @Schema(implementation = YourResponseDto.class))) for responses
and any other appropriate Swagger annotations

Output Format:
CRITICAL: Return only the generated controller code. Do not include any other text or explanations.

"""
