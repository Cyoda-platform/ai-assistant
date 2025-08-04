Analyze the workflow json and find all unique ProcessorClassNames 
        "processors": [ {
     from here --->       "name": "ProcessorClassName" 
          } ]
 Ignore any criteria/criterion 
Now for each ProcessorClassName that you've outlined in the workflow configurations,
please provide the code for it based on the prototype code and the entity pojo and call add_application_resource tool with processor name and content - processor java code.
Add processor classes exactly for each ProcessorClassName from the workflow json. No more, no less.
First check workflow json and extract all unique ProcessorClassNames. Then check the code for it.
BEFORE WRITING ANY PROCESSOR CODE:
1. Review the entity POJO structure to see what getters/setters are actually available
2. Only use properties that exist in the entity POJO - do not invent or assume properties

IMPORTANT: The processor class name and the name used in the supports() method MUST EXACTLY MATCH the processor name from the workflow configuration. Do not modify or change these names in any way.

Call add_application_resource with:
- resource_path: 'src/main/java/com/java_template/application/processor/{ProcessorClassName}.java'
- file_contents: processor java code using CyodaProcessor interface

Processor Interface Requirements

public interface CyodaProcessor {
    EntityProcessorCalculationResponse process(CyodaEventContext<EntityProcessorCalculationRequest> context);
    boolean supports(OperationSpecification modelKey);
}

Supports method implementation:

@Override
public boolean supports(OperationSpecification modelSpec) {
    return className.equalsIgnoreCase(modelSpec.operationName());
}


Processor Class Prototype (Use this pattern)

package com.java_template.application.processor;
import com.java_template.application.entity.EntityName;
import com.java_template.common.serializer.ErrorInfo;
import com.java_template.common.serializer.ProcessorSerializer;
import com.java_template.common.serializer.SerializerFactory;
import com.java_template.common.workflow.CyodaEventContext;
import com.java_template.common.workflow.CyodaProcessor;
import com.java_template.common.workflow.OperationSpecification;
import com.java_template.common.config.Config;
import org.cyoda.cloud.api.event.processing.EntityProcessorCalculationRequest;
import org.cyoda.cloud.api.event.processing.EntityProcessorCalculationResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors
import com.java_template.common.service.EntityService;
import com.java_template.common.util.SearchConditionRequest
import com.java_template.common.util.Condition;

@Component
public class ProcessorClassName implements CyodaProcessor {

    private final Logger logger = LoggerFactory.getLogger(this.getClass());
    private final ProcessorSerializer serializer;
    private final ObjectMapper objectMapper; only if needed for business logic
    private final String className = this.getClass().getSimpleName();

    public ProcessorClassName(SerializerFactory serializerFactory, ObjectMapper objectMapper (if needed)) {
        this.serializer = serializerFactory.getDefaultProcessorSerializer(); //always follow this pattern
        this.objectMapper = objectMapper;  (if needed)
    }

    @Override
    public EntityProcessorCalculationResponse process(CyodaEventContext<EntityProcessorCalculationRequest> context) {
        EntityProcessorCalculationRequest request = context.getEvent();
        logger.info("Processing EntityName for request: {}", request.getId());

        //This is a predefined chain. Just write the business logic in processEntityLogic method.
        return serializer.withRequest(request)
            .toEntity(EntityName.class)
            .validate(this::isValidEntity, "Invalid entity state")
            .map(this::processEntityLogic)
            .complete();
    }

    @Override
    public boolean supports(OperationSpecification modelSpec) {
        return className.equalsIgnoreCase(modelSpec.operationName());
    }
    private boolean isValidEntity(HNItem entity) {
       return entity != null && entity.isValid();
    }
    // CRITICAL: This method MUST contain the actual business logic from CyodaEntityControllerPrototype
    // Find the processEntityName method in CyodaEntityControllerPrototype.java and copy its logic here
    private EntityName processEntityLogic(ProcessorSerializer.ProcessorEntityExecutionContext<EntityName> context) {
           EntityName entity = context.entity();
           //String technicalId = context.request().getEntityId(); --get entity technical id if necessary
           Replace this comment with ACTUAL business logic from processEntityName method
           Example of what should be here (from prototype):
           - Data validation and transformation
           - External API calls
           - Business rule calculations
           - Field modifications and enrichment
           - Any other processing logic from the prototype method
          - You can use EntityService to fetch, add or update related entities if needed. But you cannot use com.java_template.common.service.EntityService to update the current entity. The current entity is passed as a method argument and you can modify it directly. It will be persisted automatically.
          - EntityService is a bean, so inject it via constructor if needed.
        return entity;
    }

    // Add other helper methods as needed based on the prototype logic
}

CRITICAL REQUIREMENTS:
1. **NO PLACEHOLDER CODE**: The processEntityLogic method MUST contain real business logic from CyodaEntityControllerPrototype
WHAT TO LOOK FOR IN CyodaEntityControllerPrototype.java:
- Methods that process entities (names may vary: `processUsers`, `processPets`, `handleOrders`, `transformData`, etc.)
- Private methods that contain business logic for your entity type

ONLY use existing entity properties - do not access non-existent getters/setters.


add_application_resource Tool Usage

After each processor is generated, call the add_application_resource tool like:

Exhaustive list of EntityService methods:
CompletableFuture<UUID> addItem(String entityModel, String entityVersion, Object entity);
CompletableFuture<List<UUID>> addItems(String entityModel, String entityVersion, Object entities);
CompletableFuture<ObjectNode> getItem(String entityModel, String entityVersion, UUID technicalId);
CompletableFuture<ArrayNode> getItems(String entityModel, String entityVersion);
CompletableFuture<ArrayNode> getItemsByCondition(String entityModel, String entityVersion, Object condition, boolean inMemory);
CompletableFuture<UUID> deleteItem(String entityModel, String entityVersion, UUID technicalId);
EntityService doesn't have any other methods, please do not reinvent anything else.
FINAL REMINDER - ABSOLUTELY CRITICAL:
🚨 DO NOT CREATE PROCESSORS WITH PLACEHOLDER CODE OR COMMENTS LIKE 'TODO: Add business logic'
🚨 YOU MUST FIND AND COPY THE ACTUAL BUSINESS LOGIC FROM CyodaEntityControllerPrototype.java
🚨 SEARCH FOR ENTITY PROCESSING METHODS (names may vary - not always processEntityName)
🚨 LOOK FOR METHODS REFERENCED IN entityService.addItem/s() CALLS
🚨 THE PROCESSOR MUST DO THE SAME WORK AS THE PROTOTYPE METHOD - NO SHORTCUTS
🚨 IGNORE CRITERIA FROM THE WORKFLOW - PROCESSORS ONLY
🚨 YOU CAN INJECT ONLY EntityService, SerializerFactory and ObjectMapper (if needed) via constructor. NEVER INJECT ANYTHING ELSE. NEVER REFERENCE DIRECTLY ANY CONTROLLERS OR ANY OTHER CLASSES.
🚨 THE CHANGES TO THE CURRENT ENTITY MUST BE DONE BY MODIFYING THE ENTITY OBJECT PASSED TO THE PROCESSOR METHOD. DO NOT USE entityService.addItem/updateItem/deleteItem ON THE CURRENT ENTITY.
If you cannot find any business logic methods for an entity, create a simple processor that just returns the entity unchanged, but DO NOT create placeholder code that pretends to do business logic.