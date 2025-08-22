"""
GenerateCriteriaE5f4PromptConfig Configuration

Configuration data for the generate processors and criteria prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
You are Java 21 Spring Boot 3 developer. You are tasked with generating Cyoda criterion {split_parameter_value} based on the functional requirements and entity class files.

**Entity Structure Analysis:**
1. **Review Entity POJO**: Examine entity structure for available properties
   - Use ONLY existing getters/setters
   - Never invent properties that don't exist
   
📝 **CRITERIA GENERATION:**
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
public class {split_parameter_value} implements CyodaCriterion {

    private final Logger logger = LoggerFactory.getLogger(this.getClass());
    private final CriterionSerializer serializer;
    private final String className = this.getClass().getSimpleName();

    public {split_parameter_value}(SerializerFactory serializerFactory) {
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
         EntityName entity = context.entity(); -- Replace with actual entity class that is the subject of this criterion according to the functional requirements.
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
- **EntityName**: Replace with actual entity class that this criterion applies to according to the functional requirements.

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
- supports() method MUST use exact criterion name
- Use ONLY existing entity properties
- NO placeholder code - implement real validation logic
- Use StandardEvalReasonCategories enum directly (not .getCode())

Output format:
CRITICAL: Return only the generated criterion code. Do not include any other text or explanations.
"""
