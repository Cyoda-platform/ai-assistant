"""
GenerateProcessorsAndCriteriaE5f4PromptConfig Configuration

Configuration data for the generate processors and criteria prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
You are tasked with generating Cyoda processors and criteria based on workflow configurations.

Based on the functional requirements, workflow JSON files, and controller classes provided, create the business logic processors and validation criteria.

🔍 **PHASE 1: COMPONENT EXTRACTION**

**Step 1: Extract Required Components**
Use the `extract_workflow_components` tool to identify all processors and criteria needed:
- workflow_directory: "src/main/java/com/java_template/application/workflow"
- output_format: "detailed"

This will provide you with:
- Complete list of processors to generate
- Complete list of criteria to generate
- Implementation guidance for each component

**Step 2: Analyze Extraction Results**
Review the extraction output to understand:
- Which processor classes need to be created
- Which criteria classes need to be implemented
- Business logic requirements for each component

🔍 **PHASE 2: ANALYSIS & PREPARATION**

**Entity Structure Analysis:**
1. **Review Entity POJO**: Examine entity structure for available properties
   - Use ONLY existing getters/setters
   - Never invent properties that don't exist

2. **Understand Business Logic**: Review functional requirements for validation rules
   - Look for conditional logic, business constraints
   - Identify what each criterion should validate
   - Map business rules to processor implementations

**Implementation Planning:**
- Plan processor implementations based on business logic requirements
- Design criteria validation logic based on functional requirements
- Ensure all components follow established patterns

🔍 **PHASE 3: IMPLEMENTATION**

📝 **PROCESSOR GENERATION:**

For each processor identified by the extraction tool, create using add_application_resource with:
- resource_path: 'src/main/java/com/java_template/application/processor/{ProcessorClassName}.java'
Use camelCase for ProcessorClassName, starting with capital letter
- file_contents: complete Java processor class

Processor template structure:
```java
package com.java_template.application.processor;
import com.java_template.application.entity.entityName.version_1.EntityName;
import com.java_template.common.serializer.ProcessorSerializer;
import com.java_template.common.serializer.SerializerFactory;
import com.java_template.common.workflow.CyodaEventContext;
import com.java_template.common.workflow.CyodaProcessor;
import com.java_template.common.workflow.OperationSpecification;
import org.cyoda.cloud.api.event.processing.EntityProcessorCalculationRequest;
import org.cyoda.cloud.api.event.processing.EntityProcessorCalculationResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component
public class {ProcessorClassName} implements CyodaProcessor {

    private static final Logger logger = LoggerFactory.getLogger({ProcessorClassName}.class);
    private final String className = this.getClass().getSimpleName();
    private final ProcessorSerializer serializer;

    public {ProcessorClassName}(SerializerFactory serializerFactory) {
        this.serializer = serializerFactory.getDefaultProcessorSerializer();
    }

    @Override
    public EntityProcessorCalculationResponse process(CyodaEventContext<EntityProcessorCalculationRequest> context) {
        EntityProcessorCalculationRequest request = context.getEvent();
        logger.info("Processing {EntityName} for request: {}", request.getId());

        return serializer.withRequest(request) //always use this method name to request EntityProcessorCalculationResponse
            .toEntity({EntityName}.class)
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
        // Leave detailed todo what needs to be implemented
        return entity;
    }
}
```

📝 **CRITERIA GENERATION:**

For each criteria function identified by the extraction tool, generate using this template:

```java
package com.java_template.application.criterion;

import com.java_template.application.entity.entityName.version_1.EntityName;
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
        // This is a predefined chain. Just write the business logic in processEntityLogic method.
        return serializer.withRequest(request) //always use this method name to request EntityCriteriaCalculationResponse
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
         // Implement validation logic based on business requirements
         // Example patterns:
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

🎯 REPLACEMENT RULES:
- **CriterionClassName**: Use EXACTLY from workflow JSON (no changes!)
- **EntityName**: Replace with actual entity class (Pet, User, Order)
- **entityName**: Replace with camelCase name (pet, user, order)

✅ EVALUATION OUTCOME PATTERNS:
```java
// Success
return EvaluationOutcome.success();

// Failures (use enum directly, NOT .getCode())
return EvaluationOutcome.fail("message", StandardEvalReasonCategories.VALIDATION_FAILURE);
return EvaluationOutcome.fail("message", StandardEvalReasonCategories.BUSINESS_RULE_FAILURE);
return EvaluationOutcome.fail("message", StandardEvalReasonCategories.DATA_QUALITY_FAILURE);
```

🚨 CRITICAL REQUIREMENTS:
- Class name MUST match workflow JSON exactly
- supports() method MUST use exact criterion name
- Use ONLY existing entity properties
- NO placeholder code - implement real validation logic
- Use StandardEvalReasonCategories enum directly (not .getCode())

📁 TOOL USAGE:
Call add_application_resource for each criterion:
- resource_path: 'src/main/java/com/java_template/application/criterion/{CriterionClassName}.java'
- file_contents: generated Java code

🎯 **PHASE 4: COMPLETION VERIFICATION**

**Final Validation:**
- [ ] All processors from extraction tool are implemented
- [ ] All criteria from extraction tool are implemented
- [ ] Names match workflow JSON exactly
- [ ] Only existing entity properties used
- [ ] EvaluationOutcome usage correct
- [ ] Real business logic implemented
- [ ] All imports present

**Success Criteria:**
- Every processor identified by the extraction tool has a complete Java implementation
- Every criteria function identified by the extraction tool has a complete Java implementation
- All implementations follow the established patterns and templates
- Business logic is properly implemented based on functional requirements

Generate all processors and criteria needed for the complete application functionality as identified by the workflow component extraction tool.
"""
