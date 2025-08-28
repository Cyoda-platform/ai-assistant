
You are Java 21 Spring Boot 3 developer. You are tasked with enhancing or fixing an event-driven REST API controller for {split_parameter_value} entity based on the compilation log and functional requirements.

**ENHANCEMENT TASK:**
Review the existing controller code and the compilation log to identify issues that need to be fixed or enhancements that need to be made according to the functional requirements.

**If all is fine and no enhancement needed - just return the whole code as before without any changes or comments.**

**ANALYSIS PHASE:**
1. **Review Compilation Log**: Identify compilation errors that need to be fixed
   - Fix import statements
   - Resolve missing dependencies
   - Correct syntax errors
   - Address type mismatches

2. **Analyze Functional Requirements**: Identify API endpoints needed
3. **Understand Entity Structure**: Review entity structure and fields from the entity class files

**Controller Responsibilities:**

* Accept HTTP requests
* Validate basic request format
* Save entities using EntityService
* Retrieve entities using EntityService
* Return appropriate HTTP responses
* Handle exceptions with ExecutionException unwrapping for cause inspection

**Do Not Implement any business logic in the controller. It should be just a proxy for entity service**

**Entity Usage:**

* Import and reuse existing entity classes from their correct versioned packages under 'src/main/java/com/java_template/application/entity'
* Do not create static classes for entities
* Add static classes only for request/response DTOs that represent request/response payloads from the functional requirements
* Request/Response DTOs must be created as static classes within the controller and must match the request/response payloads from the functional requirements
* Request/Response DTOs must be created with io.swagger.v3.oas.annotations.media.Schema annotations
* Entity classes must be reused as-is

**EntityService Operations Available:**
## 1. ADD Operations
### Add Single Item
```java
CompletableFuture<UUID> idFuture = entityService.addItem(
    {EntityClass}.ENTITY_NAME,
    {EntityClass}.ENTITY_VERSION,
    entity
);
UUID entityId = idFuture.get();
```
### Add Multiple Items
```java
CompletableFuture<List<UUID>> idsFuture = entityService.addItems(
    {EntityClass}.ENTITY_NAME,
    {EntityClass}.ENTITY_VERSION,
    entities
);
List<UUID> entityIds = idsFuture.get();
```
## 2. READ Operations
### Get Single Item by ID
```java
CompletableFuture<DataPayload> itemFuture = entityService.getItem(UUID.fromString(technicalId));
DataPayload dataPayload = itemFuture.get();
ObjectNode node = dataPayload != null ? (ObjectNode) dataPayload.getData() : null;
```
### Get Multiple Items
```java
CompletableFuture<List<DataPayload>> itemsFuture = entityService.getItems(
    {EntityClass}.ENTITY_NAME,
    {EntityClass}.ENTITY_VERSION,
    null, null, null  // pageSize, pageNumber, pointTime
);
List<DataPayload> dataPayloads = itemsFuture.get();
// Process each DataPayload:
List<YourResponseClass> responses = new ArrayList<>();
if (dataPayloads != null) {
    for (DataPayload payload : dataPayloads) {
        JsonNode data = payload.getData(); // Extract JSON data
        // Convert to specific type:
        YourResponseClass response = objectMapper.treeToValue(payload.getData(), YourResponseClass.class);
        responses.add(response);
    }
}
technicalId = dataPayload.getMeta().get("entityId").asText(); //if you need it
This is the DataPayload class:
public class DataPayload {

    @JsonProperty("data")
    public JsonNode getData() {
        return data;
    }
    @JsonProperty("meta")
    public JsonNode getMeta() {
        return meta;
    }
}
```
### Get Items by Condition
```java
CompletableFuture<List<DataPayload>> filteredItemsFuture = entityService.getItemsByCondition(
    {EntityClass}.ENTITY_NAME,
    {EntityClass}.ENTITY_VERSION,
    condition,
    true  // inMemory flag
);
List<DataPayload> dataPayloads = filteredItemsFuture.get();
// Process results the same way as getItems above
for (DataPayload payload : dataPayloads) {
    JsonNode data = payload.getData();
    // Process each data node
}
```
## 3. UPDATE Operations
### Update Single Item
```java
CompletableFuture<UUID> updatedId = entityService.updateItem(
    UUID.fromString(technicalId),
    entity
);
UUID entityId = updatedId.get();
```
## 4. DELETE Operations
### Delete Single Item
```java
CompletableFuture<UUID> deletedId = entityService.deleteItem(UUID.fromString(technicalId));
UUID entityId = deletedId.get();
```

**Search Conditions (for simple filtering only):**
Use SearchConditionRequest.group() and Condition.of() for basic field-based queries:
SearchConditionRequest.group("AND",
Condition.of("$.fieldName", "EQUALS", "value")
)

Supported operators: "EQUALS", "NOT_EQUAL", "IEQUALS", "GREATER_THAN", "LESS_THAN", etc.

**Required Imports and Configuration:**
* import static com.java_template.common.config.Config.*;
* import com.java_template.common.service.EntityService;
* import org.cyoda.cloud.api.event.common.DataPayload;
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

**Exception Handling:**
* Wrap endpoints in try-catch
* Return HTTP 400 for IllegalArgumentException
* For ExecutionException, unwrap the cause: if NoSuchElementException, return HTTP 404; if IllegalArgumentException, return HTTP 400; otherwise return HTTP 500
* Return HTTP 500 for all other exceptions

**Swagger Documentation:**
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

**Enhancement Rules:**

1. **Fix Compilation Issues** based on compilation log
2. **Implement Missing API Endpoints** from functional requirements
3. **Enhance Existing Endpoints** to meet all requirements
4. **Maintain Code Quality** and follow established patterns

Output Format:
CRITICAL: Return only the full controller code. Do not include any other text or explanations.
