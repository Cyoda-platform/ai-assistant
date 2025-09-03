"""
GenerateProcessorsAndCriteriaE5f4PromptConfig Configuration

Configuration data for the generate processors and criteria prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
This project is a **Cyoda client application**.

Reference:

1. Example Condition:
```java
Condition cartIdCondition = Condition.of("$.cartId", "EQUALS", cartId);
SearchConditionRequest condition = new SearchConditionRequest();
condition.setType("group");
condition.setOperator("AND");
condition.setConditions(List.of(cartIdCondition));
```

2. CRITICAL: inMemory flag in entity service requests should be set to true.

3. **CRITICAL PRINCIPLE: Entity as Payload**
   - The entity itself IS the payload - never extract data from request payload using ObjectMapper
   - Controllers should accept entity objects directly as @RequestBody, not Map<String, Object>
   - Processors should use `context.entity()` directly, never extract from `request.getPayload().getData()`
   - Never use `ObjectMapper.convertValue(request.getPayload().getData(), Map.class)`

4. Processor template structure:
```java
package com.java_template.application.processor;

import com.java_template.application.entity.entityName.version_1.EntityName; // replace with actual entity name
import com.java_template.common.serializer.ProcessorSerializer;
import com.java_template.common.serializer.SerializerFactory;
import com.java_template.common.serializer.ErrorInfo;
import com.java_template.common.workflow.CyodaEventContext;
import com.java_template.common.workflow.CyodaProcessor;
import com.java_template.common.workflow.OperationSpecification;
import org.cyoda.cloud.api.event.processing.EntityProcessorCalculationRequest;
import org.cyoda.cloud.api.event.processing.EntityProcessorCalculationResponse;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component
public class ProcessorName implements CyodaProcessor {

    private static final Logger logger = LoggerFactory.getLogger(ProcessorName.class);
    private final String className = this.getClass().getSimpleName();
    private final ProcessorSerializer serializer;

    public ProcessorName(SerializerFactory serializerFactory) {
        this.serializer = serializerFactory.getDefaultProcessorSerializer();
    }

    @Override
    public EntityProcessorCalculationResponse process(CyodaEventContext<EntityProcessorCalculationRequest> context) {
        EntityProcessorCalculationRequest request = context.getEvent();
        logger.info("Processing EntityName for request: {}", request.getId());

        return serializer.withRequest(request)
            .toEntity(EntityName.class)
            .withErrorHandler((error, entity) -> {
                logger.error("Failed to extract entity: {}", error.getMessage(), error);
                return new ErrorInfo("TO_ENTITY_ERROR", "Failed to extract entity: " + error.getMessage());
            })
            .validate(this::isValidEntity, "Invalid entity state")
            .map(this::processEntityLogic)
            .complete();
    }

    @Override
    public boolean supports(OperationSpecification modelSpec) {
        return className.equalsIgnoreCase(modelSpec.operationName());
    }

    private boolean isValidEntity(EntityName entity) {
        return entity != null && entity.isValid();
    }

    private EntityName processEntityLogic(ProcessorSerializer.ProcessorEntityExecutionContext<EntityName> context) {
        EntityName entity = context.entity();
        
        // CRITICAL: The entity already contains all the data you need
        // Never extract from request payload - use entity getters directly
        // Example: String someValue = entity.getSomeField();
        
        // Implement business logic here using entity data
        
        return entity;
    }
}
```

5. Controller template structure:
```java
@RestController
@RequestMapping("/ui/entityname")
@CrossOrigin(origins = "*")
public class EntityNameController {

    private static final Logger logger = LoggerFactory.getLogger(EntityNameController.class);
    private final EntityService entityService;

    public EntityNameController(EntityService entityService) {
        this.entityService = entityService;
    }

    @PostMapping
    public ResponseEntity<EntityResponse<EntityName>> createEntity(@RequestBody EntityName entity) {
        try {
            // CRITICAL: Pass entity directly - it IS the payload
            EntityResponse<EntityName> response = entityService.save(entity);
            logger.info("Entity created with ID: {}", response.getMetadata().getId());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("Error creating entity", e);
            return ResponseEntity.badRequest().build();
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<EntityResponse<EntityName>> updateEntity(
            @PathVariable UUID id, 
            @RequestBody EntityName entity,
            @RequestParam(required = false) String transition) {
        try {
            // CRITICAL: Pass entity directly - no payload manipulation needed
            EntityResponse<EntityName> response = entityService.update(id, entity, transition);
            logger.info("Entity updated with ID: {}", id);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("Error updating entity", e);
            return ResponseEntity.badRequest().build();
        }
    }
}
```

6. Criterion template structure:
```java
package com.java_template.application.criterion;

import com.java_template.application.entity.EntityName.version_1.EntityName;
import com.java_template.common.serializer.CriterionSerializer;
import com.java_template.common.serializer.EvaluationOutcome;
import com.java_template.common.serializer.ReasonAttachmentStrategy;
import com.java_template.common.serializer.SerializerFactory;
import com.java_template.common.serializer.StandardEvalReasonCategories;
import com.java_template.common.workflow.CyodaCriterion;
import com.java_template.common.workflow.CyodaEventContext;
import com.java_template.common.workflow.OperationSpecification;
import org.cyoda.cloud.api.event.processing.EntityCriteriaCalculationRequest;
import org.cyoda.cloud.api.event.processing.EntityCriteriaCalculationResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
public class CriterionClassName implements CyodaCriterion {

    private final Logger logger = LoggerFactory.getLogger(this.getClass());
    private final CriterionSerializer serializer;
    private final String className = this.getClass().getSimpleName();

    public CriterionClassName(SerializerFactory serializerFactory) {
        this.serializer = serializerFactory.getDefaultCriteriaSerializer();
    }

    @Override
    public EntityCriteriaCalculationResponse check(CyodaEventContext<EntityCriteriaCalculationRequest> context) {
        EntityCriteriaCalculationRequest request = context.getEvent();
        return serializer.withRequest(request)
            .evaluateEntity(EntityName.class, this::validateEntity)
            .withReasonAttachment(ReasonAttachmentStrategy.toWarnings())
            .complete();
    }

    @Override
    public boolean supports(OperationSpecification modelSpec) {
        return className.equalsIgnoreCase(modelSpec.operationName());
    }

    private EvaluationOutcome validateEntity(CriterionSerializer.CriterionEntityEvaluationContext<EntityName> context) {
        EntityName entity = context.entity();

        // CRITICAL: Use entity getters directly - never extract from payload
        // Example validation patterns:
        if (entity.getSomeField() == null) {
            return EvaluationOutcome.fail("Field is required", StandardEvalReasonCategories.VALIDATION_FAILURE);
        }
        if (!businessRuleCheck(entity)) {
            return EvaluationOutcome.fail("Business rule violated", StandardEvalReasonCategories.BUSINESS_RULE_FAILURE);
        }
        return EvaluationOutcome.success();
    }
}
```

7. **CRITICAL ANTI-PATTERNS TO AVOID:**
   - ❌ `Map<String, Object> payloadMap = objectMapper.convertValue(request.getPayload().getData(), Map.class)`
   - ❌ `@RequestBody Map<String, Object> request` in controllers
   - ❌ Manual payload extraction and entity reconstruction
   - ❌ Creating separate payload objects when entity contains the data
   - ❌ Using ObjectMapper in processors for payload extraction

8. **CORRECT PATTERNS TO USE:**
   - ✅ `EntityName entity = context.entity()` in processors
   - ✅ `@RequestBody EntityName entity` in controllers
   - ✅ `EntityResponse<EntityName> response = entityService.save(entity)`
   - ✅ Direct entity field access: `entity.getFieldName()`

9. Important: A business entity always has a technical id, which assigned by Cyoda. This id is returned with entity service save operation in EntityResponse.
   - `entityResponse.getMetadata().getState()` -- to get the state of the entity saved/retrieved with entity service
   - `entityResponse.getMetadata().getId()` -- to get the technical id of the entity saved/retrieved with entity service

However business entities can have business id as well, which is set by the user. This id is not unique and can be changed by the user.
You can also use business id to retrieve the entity.
In this case you will need to use entity service update by business id, find by business id, etc.
So you need to decide which type of id you want to use for your entity and then use proper entity service methods.

Instructions:
1. Read the code for src/main/java/com/java_template/common/service/EntityService.java, src/main/java/com/java_template/common/util/SearchConditionRequest.java, src/main/java/com/java_template/common/workflow/CyodaEntity.java, src/main/java/com/java_template/common/workflow/CyodaEventContext.java

2. Read requirements for entities in src/main/resources/functional_requirements/entities.md
Implement entities in src/main/java/com/java_template/application/entity/{entity_name}/version_1/{EntityName}.java as POJOs. Use Lombok @Data annotation.
Use constants for entity class name, entity name (always use class name), and version - always 1.
Example:
@Data
public class CatFact implements CyodaEntity {
    public static final String ENTITY_NAME = CatFact.class.getSimpleName();
    public static final Integer ENTITY_VERSION = 1;
    @Override
    public OperationSpecification getModelKey() {
        ModelSpec modelSpec = new ModelSpec();
        modelSpec.setName(ENTITY_NAME);
        modelSpec.setVersion(ENTITY_VERSION);
        return new OperationSpecification.Entity(modelSpec, ENTITY_NAME);
    }
    @Override
    public boolean isValid() {
        return true;
    }

Run compilation . Fix any compilation errors.

3. Read workflow json files in src/main/resources/workflow for workflow documentation. Understand the workflow states, transitions, processors and criteria.

4. Read requirements for processors in src/main/resources/functional_requirements/processors.md
Implement each processor following the "Entity as Payload" principle - never extract from request payload.
**CRITICAL: The entity passed to processEntityLogic already contains all the data you need.**
Implement all the necessary business logic, including calls to other entities, external APIs, etc.
You cannot update the current entity state. You can only retrieve the current state.
You cannot update this (current) entity. But you can get/update/delete other entities with EntityService.
If you update other entity be careful with the transition you use. Check the workflow documentation to understand which manual transitions are possible from the current entity state.
You can get entity id (technical id assigned by Cyoda) for the current entity from context.getEvent().getEntityId() and for other entities call entity service and get entityResponse.getMetadata().getId().
You can get entity state from context.getEvent().getPayload().getMeta().get("state") for the current entity and for other entities call entity service and get entityResponse.getMetadata().getState() for the other entity.
You are recommended to use entity technical id and not business id in the entityService calls for performance reasons.

You can also update without specifying the transition. In this case the entity will loop back to the same state it was before the update.
If you need to move to a different transition/state, you need to check the next transition in the workflow and use it in update operation. Refer to entity workflow documentation.

Make sure the generated code compiles. Fix any compilation errors. You can parallelise the work on processors, criteria and controllers.
CRITICAL: Do not use Java reflection. Use entity getters and setters only. You cannot modify code in src/main/java/com/java_template/common directory.
CRITICAL: Do compilation checks as often as possible, do not delay them.
If you need to add tests you can add them to src/test/java/com/java_template/application directory. You can leave the less tests there.

5. Implement criteria following the same principle - use entity data directly.
Implement criteria in src/main/java/com/java_template/application/criterion/{CriterionName}.java based on the requirements in src/main/resources/functional_requirements/criteria.md
Be minimalistic. Criteria should be simple.

6. Implement controllers that accept entities directly as @RequestBody, not Map<String, Object>.
**CRITICAL: Controllers should work with EntityResponse<T> and pass entities directly to EntityService.**
Implement controllers in src/main/java/com/java_template/application/controller/{EntityName}Controller.java based on the requirements in src/main/resources/functional_requirements/controllers.md

Be very precise, do not miss any requirements. The endpoints should match the requirements exactly.
Prefer using entity technical id (you can get one from entityResponse.getMetadata().getId()) over business id for performance reasons.
You can use technical id in the request and response. But you need to return the technical id in the response.
The main purpose of the controller is to proxy the requests to the entity service. There should be no business logic in the controllers.
Implement all the endpoints exactly as specified in the requirements. If there are CRUD operations that are not present in the requirements, implement them as well.
EntityService is in src/main/java/com/java_template/common/service/EntityService.java
If there are update endpoints, transition name should be nullable, the user may send null if they do not want to move to a different state.
Check in the workflow what transitions can be used for the current entity state.
You can get current entity state from the entity service response by calling entityResponse.getMetadata().getState()
You can get current entity technical id from the entity service response by calling entityResponse.getMetadata().getId()

7. **CRITICAL: Run compilation checks frequently and fix any issues immediately.**

Once you are ready check if your implementation satisfies the src/main/resources/functional_requirements/user_requirement.md.

Exit the task when all the requirements are implemented correctly silently.

"""
