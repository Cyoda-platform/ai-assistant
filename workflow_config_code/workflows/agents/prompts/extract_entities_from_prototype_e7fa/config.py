"""
ExtractEntitiesFromPrototypeE7faPromptConfig Configuration

Generated from config: workflow_configs/agents/prompts/extract_entities_from_prototype_e7fa/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """You are provided with the entities requirements document.

Please return Entity Pojo for EntityName={split_parameter_value} from the requirements document.
Entity POJO template:
package com.java_template.application.entity.{split_parameter_value_lower}.version_1;

import com.java_template.common.workflow.CyodaEntity;
import com.java_template.common.workflow.OperationSpecification;
import org.cyoda.cloud.api.event.common.ModelSpec;
import lombok.Data;

@Data
public class {split_parameter_value} implements CyodaEntity {
    public static final String ENTITY_NAME = "{split_parameter_value}"; 
    public static final Integer ENTITY_VERSION = 1;
    // Add your entity fields here

    public {split_parameter_value}() {} 

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
}

Rules:
- Add appropriate fields based on the prototype code.
- Implement proper validation logic in isValid() (e.g., use .isBlank() for String fields, not null checks for UUID fields).
- If enums are needed, use String instead.
- Ensure @Data from Lombok generates all required getters/setters.
- POST endpoints that add entities should return only a technical id.
- Use String types for foreign key references representing serialized UUIDs.

Output format (strict):
- Return ONLY Entity POJO code. No markdown formatting, no explanation. Regular Java comments (// like this) are allowed, but avoid extra narrative or markdown-style formatting.

Requirement:"""
