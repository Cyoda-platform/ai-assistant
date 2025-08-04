Generate Java criterion classes for workflow configurations that contain criteria of type 'function'.

🔍 ANALYSIS PHASE - Complete BEFORE writing any code:

1. **Extract Function Criteria**: Find all criteria in workflow JSON where:
   - "criterion": { "type": "function", "function": { "name": "CriterionClassName" } }
   - ONLY process function-type criteria, ignore others

2. **Review Entity POJO**: Examine entity structure for available properties
   - Use ONLY existing getters/setters
   - Never invent properties that don't exist

3. **Understand Business Logic**: Review prototype code for validation rules
   - Look for conditional logic, business constraints
   - Identify what the criterion should validate

📝 CODE GENERATION:

For each CriterionClassName found, generate using this template:

```java
package com.java_template.application.criterion;

import com.java_template.application.entity.EntityName;
import com.java_template.common.serializer.CriterionSerializer;
import com.java_template.common.serializer.EvaluationOutcome;
import com.java_template.common.serializer.ReasonAttachmentStrategy;
import com.java_template.common.serializer.SerializerFactory;
import com.java_template.common.serializer.StandardEvalReasonCategories;
import com.java_template.common.config.Config;
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
         Implement validation logic based on business requirements
         Example patterns:
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

🔍 FINAL VALIDATION:
- [ ] Names match workflow JSON exactly
- [ ] Only existing entity properties used
- [ ] EvaluationOutcome usage correct
- [ ] Real business logic implemented
- [ ] All imports present