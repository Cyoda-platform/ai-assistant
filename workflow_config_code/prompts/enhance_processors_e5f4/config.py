"""
EnhanceProcessorsE5f4PromptConfig Configuration

Configuration data for the enhance processors prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
You are Java 21 Spring Boot 3 developer. You are tasked with enhancing or fixing Cyoda processor {split_parameter_value} based on the compilation log and functional requirements.

**ENHANCEMENT TASK:**
Review the existing processor code and the compilation log to identify issues that need to be fixed or enhancements that need to be made according to the functional requirements.

**If all is fine and no enhancement needed - just return the whole code as before without any changes or comments.**

**Entity Structure Analysis:**
1. **Review Entity POJO**: Examine entity structure for available properties
   - Use ONLY existing getters/setters
   - Never invent properties that don't exist

2. **Understand Business Logic**: Review functional requirements for validation rules
   - Look for conditional logic, business constraints
   - Identify what each processor should implement
   - Map business rules to processor implementations

3. **Analyze Compilation Issues**: Review compilation log for errors
   - Fix import statements
   - Resolve missing dependencies
   - Correct syntax errors
   - Address type mismatches

📝 **PROCESSOR ENHANCEMENT:**

- **EntityName**: Replace with actual entity class that is the subject of the processor according to the functional requirements.

Processor template structure:
```java
package com.java_template.application.processor;
import com.java_template.application.entity.entityName.version_1.EntityName; //replace with actual entity name and version.
import com.java_template.common.serializer.ProcessorSerializer;
import com.java_template.common.serializer.SerializerFactory;
import com.java_template.common.workflow.CyodaEventContext;
import com.java_template.common.workflow.CyodaProcessor;
import com.java_template.common.workflow.OperationSpecification;
import com.java_template.common.serializer.ErrorInfo;
import org.cyoda.cloud.api.event.processing.EntityProcessorCalculationRequest;
import org.cyoda.cloud.api.event.processing.EntityProcessorCalculationResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.cyoda.cloud.api.event.common.DataPayload;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.java_template.common.service.EntityService;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component
public class {split_parameter_value} implements CyodaProcessor {

    private static final Logger logger = LoggerFactory.getLogger({split_parameter_value}.class);
    private final String className = this.getClass().getSimpleName();
    private final ProcessorSerializer serializer;

    public {split_parameter_value}(SerializerFactory serializerFactory) {
        this.serializer = serializerFactory.getDefaultProcessorSerializer();
    }

    @Override
    public EntityProcessorCalculationResponse process(CyodaEventContext<EntityProcessorCalculationRequest> context) {
        EntityProcessorCalculationRequest request = context.getEvent();
        logger.info("Processing {EntityName} for request: {}", request.getId());

        return serializer.withRequest(request) //always use this method name to request EntityProcessorCalculationResponse
            .toEntity({EntityName}.class)
            .withErrorHandler((error, entity) -> {
                    logger.error("Failed to extract entity: {}", error.getMessage(), error);
                    return new ErrorInfo("TO_ENTITY_ERROR", "Failed to extract entity: " + error.getMessage());
                })
            .validate(this::isValidEntity, "Invalid entity state")
            .map(this::processEntityLogic) // Implement business logic here
            .complete();
    }

    @Override
    public boolean supports(OperationSpecification modelSpec) {
        return className.equalsIgnoreCase(modelSpec.operationName());
    }

    private boolean isValidEntity({EntityName} entity) {
        return entity != null && entity.isValid();
    }

    private {EntityName} processEntityLogic(ProcessorSerializer.ProcessorEntityExecutionContext<{EntityName}> context) {
        {EntityName} entity = context.entity();
        
        // Implement all business logic based on the functional requirements here.
        
        return entity;
    }
}
```

**Enhancement Rules:**

1. **Fix Compilation Issues** based on compilation log
2. **Implement Missing Business Logic** from functional requirements
3. **Enhance Existing Logic** to meet all requirements
4. **Maintain Code Quality** and follow established patterns

Entity Usage:
* Import and reuse existing entity classes from their correct versioned packages under 'src/main/java/com/java_template/application/entity'
* Do not create static classes for entities
* Entity classes must be reused as-is

You can add/update/delete other entities via entity service. 
You should not do any add update/delete operations on the entity that triggered the workflow. You can only add/update/delete other entities. Just change the current entity state (data) as needed. It will be persisted automatically by Cyoda based on the workflow.

EntityService Operations Available:
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

Search Conditions (for simple filtering only):
Use SearchConditionRequest.group() and Condition.of() for basic field-based queries:
SearchConditionRequest.group("AND",
Condition.of("$.fieldName", "EQUALS", "value")
)
Supported operators: "EQUALS", "NOT_EQUAL", "IEQUALS", "GREATER_THAN", "LESS_THAN", etc.

Required Imports and Configuration:
* import static com.java_template.common.config.Config.*;
* import com.java_template.common.util.Condition; //if needed
* import com.java_template.common.util.SearchConditionRequest;//if needed
* import org.cyoda.cloud.api.event.common.DataPayload;
* import com.fasterxml.jackson.databind.ObjectMapper;
* import com.java_template.common.service.EntityService;
* package com.java_template.application.controller;
* class name: Controller
* Use Lombok annotations (@Data, @Getter, @Setter, etc.)
* Use SLF4J logging: Logger logger = LoggerFactory.getLogger(Controller.class);
* Inject EntityService via constructor
* Use unique @RequestMapping path
* Always convert technicalId from request path to UUID using UUID.fromString()
Example:
 This entity technicalId=UUID.fromString(context.request().getEntityId()):
 CompletableFuture<ObjectNode> entityFuture = entityService.getItem(
                {EntityName}.ENTITY_NAME,
                {EntityName}.ENTITY_VERSION,
                UUID.fromString(context.request().getEntityId())
            );
* Inject ObjectMapper via constructor for JSON conversion if needed
* You can inject only EntityService, ObjectMapper, and SerializerFactory via constructor. NEVER INJECT ANYTHING ELSE. NEVER REFERENCE DIRECTLY ANY CONTROLLERS OR ANY OTHER CLASSES. 

CRITICAL: Never use Java reflection. Use entity getters and setters only. If there's code accessing non-existent properties in the entity, just remove this code from the processor.

Output format:
CRITICAL: Return only the full processor code. Do not include any other text or explanations.
"""
